import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings

security = HTTPBearer(auto_error=False)

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    if token is None:
        raise HTTPException(status_code=401, detail="Нет токена доступа")

    try:
        payload = jwt.decode(token.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username = payload.get("username")

        if not username:
            raise HTTPException(status_code=401, detail="Неверный токен доступа")

        return username

    except Exception:
        raise HTTPException(status_code=401, detail="Неверный токен доступа")