from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Пример модели:
from sqlalchemy import Column, Integer, BigInteger, String, Text, ForeignKey, DateTime

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(Text, nullable=False)
    registration_date = Column(DateTime, nullable=False)


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    item_name = Column(Text, nullable=False)
    quantity = Column(BigInteger, nullable=False)  # <--- здесь BIGINT
    status = Column(Text, default='new')
    created_at = Column(DateTime, nullable=False)
