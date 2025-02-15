from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import get_db
from app.models.user import User
from app.models.merch_purchase import MerchPurchase
from app.models.coins_transaction import CoinsTransaction

router = APIRouter()

@router.get("/history")
def wallet_history(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
         raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    incoming = db.query(CoinsTransaction).filter(CoinsTransaction.recipient_id==user.id).all()
    outgoing = db.query(CoinsTransaction).filter(CoinsTransaction.sender_id==user.id).all()
    
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
def get_purchases(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
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
    
    return {"username": username, "purchases": purchase_list}