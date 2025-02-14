import jwt
import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import get_db
from app.models.user import User
from app.config import settings

router = APIRouter()

def create_access_token(username: str):
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

@router.post("/login")
def login(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = User(username=username, coins=settings.INITIAL_COINS)
        db.add(user)
        db.commit()
        db.refresh(user)
    access_token = create_access_token(username=user.username)
    return {"username": user.username, "coins": user.coins, "access_token": access_token}