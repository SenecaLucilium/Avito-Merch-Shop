from sqlalchemy import Column, Integer, String
from app import Base
from app.config import settings

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    coins = Column(Integer, default=settings.INITIAL_COINS)