"""
REST API endpoints for chat messages.
"""
from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.service import ChatService
from app.chat.schemas import (
    MessageCreate, MessageUpdate, MessageResponse,
    PaginatedMessages, ReactionCreate
)
from app.models.user import User
from app.core.database import get_db
from app.api.deps import get_current_user


router = APIRouter(prefix="/messages", tags=["Chat Messages"])


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message to a room."""
    service = ChatService(db)
    return await service.send_message(message_data, current_user)


@router.get("/room/{room_id}", response_model=PaginatedMessages)
async def get_room_messages(
    room_id: int,
    limit: int = Query(50, ge=1, le=100),
    before_id:  Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a room with pagination."""
    service = ChatService(db)
    return await service.get_messages(room_id, current_user, limit, before_id)


@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: int,
    message_data: MessageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a message (sender only)."""
    service = ChatService(db)
    return await service.update_message(message_id, message_data, current_user)


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a message (sender or admin)."""
    service = ChatService(db)
    await service.delete_message(message_id, current_user)


@router.post("/{message_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_message_read(
    message_id: int,
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark message as read."""
    service = ChatService(db)
    await service.mark_as_read(room_id, message_id, current_user)
