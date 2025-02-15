from app import engine, Base
from app.models.user import User
from app.models.merch_purchase import MerchPurchase
from app.models.coins_transaction import CoinsTransaction

Base.metadata.create_all(bind=engine)