from app import engine, Base
from app.models.user import User
from app.models.merch_purchase import MerchPurchase

Base.metadata.create_all(bind=engine)