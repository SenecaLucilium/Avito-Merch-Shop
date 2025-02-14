import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app import Base
from app.models.user import User

class MerchPurchase(Base):
    __tablename__ = "merch_purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    item = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    purchased_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))