from fastapi import APIRouter,Depends,HTTPException,BackgroundTasks
from fastapi.params import Query
from database import get_db
from sqlalchemy.orm import Session,joinedload
from models import Post,User
from schemas import PostAndUserResponse, PostCreate,PostResponse
from dependecies import get_current_user
from typing import Literal
import time

privateRouter = APIRouter(prefix="/posts", tags=["Post"], dependencies=[Depends(get_current_user)])
publicRouter = APIRouter(prefix="/posts", tags=["Post"])

@publicRouter.get("", response_model=list[PostAndUserResponse])
def get_posts_and_users(sort:str = "id",order:Literal["asc","desc"] = "asc",search:str = "",user_id: None | int = Query(default=None),limit: int = Query(default=10, ge=1, le=100), offset:int = Query(default=0, ge=0),db:Session = Depends(get_db)):
    columns = {
        "id":Post.id,
        "title":Post.title,
    }
    column = columns.get(sort)
    if column is None:
        raise HTTPException(status_code=422, detail="You can't order by this column")
    
    order_column = column.asc() if order == "asc" else column.desc()

    baseQuery = db.query(Post).options(joinedload(Post.user))
    if user_id is not None:
        baseQuery = baseQuery.filter(Post.user_id == user_id)

    return baseQuery.filter(Post.title.like(f"%{search}%")).order_by(order_column).limit(limit).offset(offset).all()
    
def get_post_by_id(post_id:int,current_user:User = Depends(get_current_user),db:Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        if post.user_id == current_user.id or current_user.role == "admin":
            return post
        else:
            raise HTTPException(status_code=403, detail="You can't view this post")
    else:
        raise HTTPException(status_code=404, detail="Post not found")

@privateRouter.get("/{post_id}", response_model=PostAndUserResponse)
def get_post(post:Post = Depends(get_post_by_id)):
    return post

def send_notification(email: str, post_title: str):
    time.sleep(5)
    print(f"Notifica inviata a {email}: nuovo post '{post_title}'")

@privateRouter.post("",response_model=PostResponse)
def add_post(post:PostCreate , background_tasks:BackgroundTasks,current_user:User = Depends(get_current_user),db:Session = Depends(get_db)):
    newPost = Post(title = post.title, content = post.content, user = current_user)
    db.add(newPost)
    db.commit()
    db.refresh(newPost)

    background_tasks.add_task(send_notification,current_user.email, newPost.title)
    return newPost

@privateRouter.put("/{post_id}")
def update_post(newPost:PostCreate,post:Post = Depends(get_post_by_id), current_user:User = Depends(get_current_user),db:Session = Depends(get_db)):
    if current_user.id == post.user_id or current_user.role == "admin":
        post.title = newPost.title
        post.content = newPost.content
        db.commit()
        db.refresh(post)
        return post
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to update this post")

@privateRouter.delete("/{post_id}", response_model=PostResponse)
def delete_post(post:Post = Depends(get_post_by_id), current_user:User = Depends(get_current_user), db:Session = Depends(get_db)):
    if post.user_id == current_user.id or current_user.role == "admin":
        db.delete(post)
        db.commit()
        return post
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to delete this post")