from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app import get_db
from app.models.user import User
from app.models.merch_purchase import MerchPurchase
from app.models.coins_transaction import CoinsTransaction
from app.utils.auth import get_current_user

router = APIRouter()

@router.get("/history")
def wallet_history(current_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    incoming = db.query(CoinsTransaction).filter(CoinsTransaction.recipient_id == user.id).all()
    outcomming = db.query(CoinsTransaction).filter(CoinsTransaction.sender_id == user.id).all()

    incoming_summary = {}
    for transaction in incoming:
        sender = db.query(User).filter(User.id == transaction.sender_id).first()

        if sender:
            incoming_summary[sender.username] = incoming_summary.get(sender.username, 0) + transaction.amount

    outcoming_summary = {}
    for transaction in outcomming:
        recipient = db.query(User).filter(User.id == transaction.recipient_id).first()

        if recipient:
            outcoming_summary[recipient.username] = outcoming_summary.get(recipient.username, 0) + transaction.amount

    return {"incoming": incoming_summary, "outcoming": outcoming_summary}

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
    
    received = []
    for tx in incoming_txs:
        sender = db.query(User).filter(User.id == tx.sender_id).first()
        if sender:
            received.append({"fromUser": sender.username, "amount": tx.amount})

    sent_txs = db.query(CoinsTransaction).filter(CoinsTransaction.sender_id == user.id).all()

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