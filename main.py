from fastapi import FastAPI, Depends
from routers import users,posts,auth
from models import User
from dependecies import get_current_user,get_current_admin

#Per avviare script: fastapi dev main.py

app = FastAPI()
app.include_router(auth.router)
app.include_router(users.privateRouter)
app.include_router(users.publicRouter)
app.include_router(posts.privateRouter)
app.include_router(posts.publicRouter)

@app.get("/")
def home():
    return {"message": "API is running"}

@app.get("/test-auth")
def test_auth(payload = Depends(get_current_user)):
    return payload

@app.get("/admin-test")
def admin_test(user: User = Depends(get_current_admin)):
    return {
        "message": "You are an admin",
        "user": user.name
    }