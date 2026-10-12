from schemas import LoginRequest,Token
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Depends, APIRouter
from security import password_hash,create_token
from database import get_db
from models import User
from schemas import UserCreate

router = APIRouter(tags=["Auth"])

@router.post("/login", response_model=Token)
def login(user:LoginRequest, db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        if not password_hash.verify(user.password,db_user.password_hash):
            raise HTTPException(status_code=401, detail="Email or password wrong")
        
        token = create_token(db_user)
        return {"access_token": token,"token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Email or password wrong")

@router.post("/signup", response_model=Token)
def signup(user:UserCreate, db:Session = Depends(get_db)):
    try:
        psw_hash = password_hash.hash(user.password)
        new_user = User(name = user.name, email = user.email, bio = user.bio, password_hash = psw_hash, role = "user")
        db.add(new_user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    else:
       db.refresh(new_user)
       token = create_token(new_user)
       return {"access_token": token,"token_type": "bearer"}