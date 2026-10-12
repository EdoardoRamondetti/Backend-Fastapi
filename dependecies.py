from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from fastapi import Depends,HTTPException
from models import User
from sqlalchemy.orm import Session
from database import get_db
from security import decode_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(status_code=401,detail="Invalid or expired token")

    user_id = int(payload.get("sub"))
    current_user = db.query(User).filter(User.id == user_id).first()

    if current_user is None:
        raise HTTPException(status_code=401,detail="User not found")

    return current_user

def get_current_admin(user: User = Depends(get_current_user)):
    if user.role == "admin":
        return user
    else:
        raise HTTPException(status_code=403, detail="Not enought permissions")