import jwt
import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app import get_db
from app.models.user import User
from app.config import settings

router = APIRouter()

class AuthRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    token: str

def create_access_token(username: str):
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"username": username, "exp": expire}

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

@router.post("/", response_model=AuthResponse)
def login(auth: AuthRequest, db: Session = Depends(get_db)):

    if not auth.username or not auth.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя пользователя и пароль не могут быть пустыми"
        )
    
    user = db.query(User).filter(User.username == auth.username).first()

    if not user:
        user = User(username=auth.username, coins=settings.INITIAL_COINS)

        db.add(user)
        db.commit()

        db.refresh(user)
    
    return {"token": create_access_token(user.username)}