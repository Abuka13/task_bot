from sqlalchemy import URL, create_engine

url_object = URL.create(
    "postgresql+pg8000",
    username="postgres",
    password="Takanashi_13",  # plain (unescaped) text
    host="localhost",
    database="query_history",
)

engine = create_engine(url_object)
with engine.connect() as connection:
    connection.execute("INSERT INTO query_history VALUES(1234,'2024-03-09',1234)")
    connection.commit()  # commits "some statement"