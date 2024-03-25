from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
Base = declarative_base()

class QueryHistory(Base):
    __tablename__ = 'query_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    timestamp = Column(DateTime, server_default=func.now())
    article = Column(String)