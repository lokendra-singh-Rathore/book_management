"""
REST API endpoints for chat rooms.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.service import ChatService
from app.chat.schemas import (
    RoomCreate, RoomUpdate, RoomResponse, RoomDetailResponse,
    AddParticipant
)
from app.models.user import User
from app.core.database import get_db
from app.api.deps import get_current_user


router = APIRouter(prefix="/rooms", tags=["Chat Rooms"])


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: RoomCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat room."""
    service = ChatService(db)
    room = await service.create_room(room_data, current_user)
    return RoomResponse.model_validate(room)


@router.get("", response_model=List[RoomResponse])
async def get_user_rooms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all rooms user is part of."""
    service = ChatService(db)
    return await service.get_user_rooms(current_user)


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific room details."""
    service = ChatService(db)
    room = await service.get_room(room_id, current_user)
    return RoomResponse.model_validate(room)


@router.put("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: int,
    room_data: RoomUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update room (admin/owner only)."""
    service = ChatService(db)
    room = await service.update_room(room_id, room_data, current_user)
    return RoomResponse.model_validate(room)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete room (owner only)."""
    service = ChatService(db)
    await service.delete_room(room_id, current_user)
