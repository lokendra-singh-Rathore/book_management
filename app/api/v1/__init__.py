from fastapi import APIRouter
from app.api.v1 import auth, books
from app.chat.routes import chat_router

api_router = APIRouter(prefix="/v1")

# Include all v1 routers
api_router.include_router(auth.router)
api_router.include_router(books.router)
api_router.include_router(chat_router)  # Chat endpoints
