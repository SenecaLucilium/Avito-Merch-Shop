from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import get_db
from app.models.user import User

router = APIRouter()

@router.post("/transfer")
def transfer_coins(sender: str, recipient: str, amount: int, db: Session = Depends(get_db)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Сумма перевода должна быть больше нуля")
    
    sender_user = db.query(User).filter(User.username == sender).first()
    if not sender_user:
        raise HTTPException(status_code=404, detail="Пользователь-отправитель не найден")
    
    recipient_user = db.query(User).filter(User.username == recipient).first()
    if not recipient_user:
        raise HTTPException(status_code=404, detail="Пользователь-получатель не найден")
    
    if sender_user.coins < amount:
        raise HTTPException(status_code=400, detail="Недостаточно монет для перевода")
    
    sender_user.coins -= amount
    recipient_user.coins += amount
    db.commit()
    
    return {
        "sender": sender_user.username,
        "recipient": recipient_user.username,
        "transferred": amount,
        "sender_balance": sender_user.coins,
        "recipient_balance": recipient_user.coins,
    }