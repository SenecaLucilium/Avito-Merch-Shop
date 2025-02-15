import jwt
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app import get_db
from app.models.user import User
from app.models.merch_purchase import MerchPurchase
from app.models.coins_transaction import CoinsTransaction
from app.config import settings

router = APIRouter()
security = HTTPBearer(auto_error=False)

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    if token is None:
        raise HTTPException(status_code=401, detail="Нет токена доступа")
    try:
        payload = jwt.decode(token.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Неверный токен доступа")
        return username
    except Exception:
        raise HTTPException(status_code=401, detail="Неверный токен доступа")

@router.get("/history")
def wallet_history(current_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    incoming = db.query(CoinsTransaction).filter(CoinsTransaction.recipient_id == user.id).all()
    outgoing = db.query(CoinsTransaction).filter(CoinsTransaction.sender_id == user.id).all()

    incoming_summary = {}
    for trans in incoming:
        sender = db.query(User).filter(User.id == trans.sender_id).first()
        if sender:
            incoming_summary[sender.username] = incoming_summary.get(sender.username, 0) + trans.amount

    outgoing_summary = {}
    for trans in outgoing:
        recipient = db.query(User).filter(User.id == trans.recipient_id).first()
        if recipient:
            outgoing_summary[recipient.username] = outgoing_summary.get(recipient.username, 0) + trans.amount

    return {"incoming": incoming_summary, "outgoing": outgoing_summary}

@router.get("/purchases")
def get_purchases(current_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    purchases = db.query(MerchPurchase).filter(MerchPurchase.user_id == user.id).all()
    purchase_list = [
        {
            "item": purchase.item,
            "price": purchase.price,
            "purchased_at": purchase.purchased_at
        }
        for purchase in purchases
    ]

    return {"username": current_username, "purchases": purchase_list}

@router.get("/info")
def get_info(current_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    purchases = db.query(MerchPurchase).filter(MerchPurchase.user_id == user.id).all()
    inventory = {}
    for purchase in purchases:
        inventory[purchase.item] = inventory.get(purchase.item, 0) + 1

    incoming_txs = db.query(CoinsTransaction).filter(CoinsTransaction.recipient_id == user.id).all()
    sent_txs = db.query(CoinsTransaction).filter(CoinsTransaction.sender_id == user.id).all()

    received = []
    for tx in incoming_txs:
        sender = db.query(User).filter(User.id == tx.sender_id).first()
        if sender:
            received.append({"fromUser": sender.username, "amount": tx.amount})

    sent = []
    for tx in sent_txs:
        recipient = db.query(User).filter(User.id == tx.recipient_id).first()
        if recipient:
            sent.append({"toUser": recipient.username, "amount": tx.amount})

    return {
        "coins": user.coins,
        "inventory": [{"type": item, "quantity": quantity} for item, quantity in inventory.items()],
        "coinHistory": {"received": received, "sent": sent}
    }