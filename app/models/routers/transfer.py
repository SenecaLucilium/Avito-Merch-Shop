from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import get_db
from app.models.user import User
from app.models.coins_transaction import CoinsTransaction
from app.models.routers.history import get_current_user
from pydantic import BaseModel

router = APIRouter()

class SendCoinRequest(BaseModel):
    toUser: str
    amount: int

@router.post("/sendCoin")
def send_coin(request: SendCoinRequest, current_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    sender_username = current_username

    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Сумма перевода должна быть больше нуля")

    sender_user = db.query(User).filter(User.username == sender_username).first()
    if not sender_user:
        raise HTTPException(status_code=404, detail="Пользователь-отправитель не найден")

    recipient_user = db.query(User).filter(User.username == request.toUser).first()
    if not recipient_user:
        raise HTTPException(status_code=404, detail="Пользователь-получатель не найден")

    if sender_user.coins < request.amount:
        raise HTTPException(status_code=400, detail="Недостаточно монет для перевода")

    sender_user.coins -= request.amount
    recipient_user.coins += request.amount

    transaction = CoinsTransaction(
        sender_id=sender_user.id,
        recipient_id=recipient_user.id,
        amount=request.amount,
        transaction_type="transfer"
    )
    db.add(transaction)
    db.commit()

    return {
        "sender": sender_username,
        "recipient": recipient_user.username,
        "transferred": request.amount,
        "sender_balance": sender_user.coins,
        "recipient_balance": recipient_user.coins,
    }