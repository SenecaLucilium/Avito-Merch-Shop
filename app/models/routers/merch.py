import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import get_db
from app.models.user import User
from app.models.merch_purchase import MerchPurchase
from app.models.coins_transaction import CoinsTransaction
from app.models.routers.history import get_current_user

router = APIRouter()

MERCH_ITEMS = {
    "t-shirt": 80,
    "cup": 20,
    "book": 50,
    "pen": 10,
    "powerbank": 200,
    "hoody": 300,
    "umbrella": 200,
    "socks": 10,
    "wallet": 50,
    "pink-hoody": 500
}

@router.get("/buy/{item}")
def buy_merch( item: str, current_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if item not in MERCH_ITEMS:
        raise HTTPException(status_code=404, detail="Мерч не найден")
    
    price = MERCH_ITEMS[item]
    if user.coins < price:
        raise HTTPException(status_code=400, detail="Недостаточно монет для покупки")
    
    user.coins -= price
    purchase = MerchPurchase(
        user_id=user.id,
        item=item,
        price=price,
        purchased_at=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(purchase)
    transaction = CoinsTransaction(
        sender_id=user.id,
        recipient_id=None,
        amount=price,
        transaction_type="purchase"
    )
    db.add(transaction)
    db.commit()
    db.refresh(purchase)
    
    return {
        "username": current_username,
        "purchased_item": item,
        "price": price,
        "remaining_coins": user.coins,
        "purchased_at": purchase.purchased_at
    }