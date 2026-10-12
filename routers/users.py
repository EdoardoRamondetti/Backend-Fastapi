from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User,Post
from sqlalchemy.exc import IntegrityError
from schemas import UserCreate, UserResponse, PostResponse
from security import password_hash
from dependecies import get_current_user

privateRouter = APIRouter(prefix="/users", tags=["User"], dependencies=[Depends(get_current_user)])
publicRouter = APIRouter(prefix="/users", tags=["User"])

@publicRouter.get("", response_model = list[UserResponse])
def get_users(db:Session = Depends(get_db)):
    return db.query(User).all()

#@router.get("/{user_id}", response_model=UserCreate)
#def get_user(user_id:int, db:Session = Depends(get_db)):
    #user = db.query(User).filter(User.id == user_id).first()
    #if user:
        #return user
    #else:
        #raise HTTPException(status_code=404, detail="User not found")

def get_user_by_id(user_id: int,db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")

@privateRouter.get("/{user_id}", response_model=UserResponse)
def get_user_info(user:User = Depends(get_user_by_id)):
    return user

@privateRouter.get("/{user_id}/name")
def get_user_name(user:User = Depends(get_user_by_id)):
    return {"name": user.name}

@privateRouter.get("/{user_id}/posts", response_model=list[PostResponse])
def get_posts_by_user(user_id:int, db:Session = Depends(get_db)):
    posts = db.query(Post).join(User).filter(User.id == user_id).all()
    if posts:
        return posts
    else: 
        raise HTTPException(status_code=404, detail="posts not found")

@privateRouter.post("", response_model=UserResponse)
def add_user(user:UserCreate, db:Session = Depends(get_db)):
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
        return new_user

@privateRouter.put("/{user_id}", response_model=UserResponse)
def update_user(newUser: UserCreate, user:User = Depends(get_user_by_id), current_user:User = Depends(get_current_user), db:Session = Depends(get_db)):
    if user.id == current_user.id or (current_user.role == "admin"):
        user.name = newUser.name
        user.email = newUser.email
        db.commit()
        db.refresh(user)
        return user
    else:
        raise HTTPException(status_code=403, detail="You can't update this user")

@privateRouter.delete("/{user_id}", response_model=UserResponse)
def delete_user(user:User = Depends(get_user_by_id), current_user=Depends(get_current_user), db:Session = Depends(get_db)):
    if current_user.id == 1 and user.id == 2:
        print(user.id == current_user.id or (current_user.role == "admin" and user.id != current_user.id))
    if user.id == current_user.id and current_user.role != "admin" or (current_user.role == "admin" and user.id != current_user.id):
        db.delete(user)
        db.commit()
        return user
    else:
        raise HTTPException(status_code=403,detail="you can't delete this user")