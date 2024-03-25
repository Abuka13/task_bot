import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor,exceptions
from sqlalchemy import URL, create_engine
from datetime import datetime
# Устанавливаем уровень логгирования
logging.basicConfig(level=logging.INFO)
subscriptions = {}
# Создаем бота и диспетчера
bot = Bot(token="7106541140:AAGhRsNT1h5m2mPaumxBucqJHnEuMKhWS7g")
dp = Dispatcher(bot)


url_object = URL.create(
    "postgresql+pg8000",
    username="postgres",
    password="Takanashi_13",  # plain (unescaped) text
    host="localhost",
    database="query_history",
)

engine = create_engine(url_object)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Получить информацию по товару", callback_data='get_info'),
        InlineKeyboardButton("Остановить уведомления", callback_data='stop_notifications'),
        InlineKeyboardButton("Получить информацию из БД", callback_data='get_info_from_db'),
        InlineKeyboardButton("Подписаться", callback_data='subscribe')

    ]
    keyboard.add(*buttons)
    await message.reply("Выберите действие:", reply_markup=keyboard)
def get_product_info(article):
    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={article}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'products' in data['data'] and len(data['data']['products']) > 0:
            product = data['data']['products'][0]
            product_info = {
                "Название": product['name'],
                "Артикул": product['id'],
                "Цена": product['salePriceU'],
                "Рейтинг": product['reviewRating'],
                "Количество на складах": product['sizes'][0]['stocks'][0]['qty']
            }
            return product_info
        else:
            return None
    else:
        return None
@dp.message_handler(lambda message: message.text.isdigit(), state='*')
async def get_wildberries_info(message: types.Message):
    article = message.text
    user_id = message.from_user.id
    product_info = get_product_info(article)
    if product_info:
        await message.answer(f"Информация о товаре:\n{product_info}")

        with engine.connect() as connection:
            connection.execute("""INSERT INTO query_history (user_id, timestamp, article)
                    VALUES (int(user_id), current_timestamp, int(article));""")
            connection.commit()
    else:
        await message.answer("Не удалось получить информацию о товаре. Попробуйте позже.")
async def send_notifications():
    while True:
        for user_id, product_info in subscriptions.items():
            try:
                await bot.send_message(user_id, f"Информация о товаре:\n{product_info}")
            except exceptions.BotBlocked:
                print(f"User {user_id} has blocked the bot.")
                subscriptions.pop(user_id, None)
        await asyncio.sleep(10 )  # 5 minutes


@dp.callback_query_handler(lambda callback_query: True)
async def process_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    if callback_query.data == 'get_info':
        await bot.send_message(callback_query.from_user.id, "Введите артикул товара с Wildberries:")
    elif callback_query.data == 'stop_notifications':
        await bot.send_message(callback_query.from_user.id, "Уведомления остановлены.")
    elif callback_query.data == 'get_info_from_db':
        await bot.send_message(callback_query.from_user.id, "Информация из БД: ...")

    elif callback_query.data == 'subscribe':
        user_id = callback_query.from_user.id
        await bot.send_message(user_id, "Вы подписаны на уведомления.")




# Запускаем бота
if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.create_task(send_notifications())
    executor.start_polling(dp, skip_updates=True)