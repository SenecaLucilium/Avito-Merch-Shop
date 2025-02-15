import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app import Base
from app.models.user import User

class CoinsTransaction(Base):
    __tablename__ = "coin_transactions"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey(User.id), nullable=False)

    recipient_id = Column(Integer, ForeignKey(User.id), nullable=True)
    amount = Column(Integer, nullable=False)

    transaction_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))