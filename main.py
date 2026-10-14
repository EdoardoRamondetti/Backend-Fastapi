from fastapi import FastAPI, Depends,Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import users,posts,auth
from models import User
from dependecies import get_current_user,get_current_admin
import logging_config

#Per avviare script: fastapi dev main.py

logger = logging_config.logging.getLogger(__name__)
logger.info("Applicazione avviata")

app = FastAPI()
app.include_router(auth.router)
app.include_router(users.privateRouter)
app.include_router(users.publicRouter)
app.include_router(posts.privateRouter)
app.include_router(posts.publicRouter)

#Middleware CORS di esempio per angular

@app.exception_handler(Exception)
def global_exception_handler(request,exception):
    logger.exception("Errore non gestito durante la richiesta: %s %s",request.method, request.url.path)
    return JSONResponse(content={"detail":"Internal server error"},status_code=500)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Metodo HTTP: {request.method}")
    logger.info(f"Url: {request.url.path}")

    response = await call_next(request)

    logger.info(f"Status code: {response.status_code}")
    return response

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