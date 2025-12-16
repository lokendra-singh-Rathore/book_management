"""
Chat routes package.
"""
from fastapi import APIRouter

from app.chat.routes import rooms, messages, websocket


# Create main chat router
chat_router = APIRouter(prefix="/chat")

# Include sub-routers
chat_router.include_router(rooms.router)
chat_router.include_router(messages.router)
chat_router.include_router(websocket.router)


__all__ = ["chat_router"]
