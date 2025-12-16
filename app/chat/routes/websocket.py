"""
WebSocket endpoint for real-time chat.
"""
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.connection_manager import connection_manager
from app.chat.service import ChatService
from app.chat.schemas import (
    WSMessageSend, WSTypingIndicator, WSJoinRoom,
    WSLeaveRoom, WSMarkRead, MessageCreate
)
from app.models.user import User
from app.core.database import get_db
from app.core.security import decode_token
from app.repositories.user import UserRepository


logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSocket"])


async def get_current_user_ws(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Authenticate user from WebSocket query parameter.
    
    Usage: ws://localhost:8000/api/v1/chat/ws?token=<jwt_token>
    """
    try:
        payload = decode_token(token)
        if not payload:
            return None
        
        email = payload.get("sub")
        if not email:
            return None
        
        user_repo = UserRepository(db)
        user = await user_repo.get_by_email(email)
        return user
    except Exception as e:
        logger.error(f"WebSocket auth error: {e}")
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time chat.
    
    **Authentication**: Pass JWT token as query parameter
    
    **Message Types (Client → Server)**:
    - `send_message`: Send a message to a room
    - `typing`: User typing indicator
    - `join_room`: Subscribe to room updates
    - `leave_room`: Unsubscribe from room
    - `mark_read`: Mark messages as read
    
    **Message Types (Server → Client)**:
    - `new_message`: New message in subscribed room
    - `message_updated`: Message was edited
    - `message_deleted`: Message was deleted
    - `user_typing`: User is typing
    - `user_presence`: User online/offline status
    - `error`: Error message
    """
    # Authenticate user
    user = await get_current_user_ws(token, db)
    
    if not user:
        await websocket.close(code=1008, reason="Authentication failed")
        return
    
    # Accept connection
    await connection_manager.connect(websocket, user.id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(message, user, websocket, db)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}", exc_info=True)
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        await connection_manager.disconnect(user.id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user.id}: {e}", exc_info=True)
        await connection_manager.disconnect(user.id)


async def handle_websocket_message(
    data: dict,
    user: User,
    websocket: WebSocket,
    db: AsyncSession
):
    """Handle incoming WebSocket messages."""
    message_type = data.get("type")
    
    if message_type == "send_message":
        await handle_send_message(data, user, db)
    
    elif message_type == "typing":
        await handle_typing(data, user)
    
    elif message_type == "join_room":
        await handle_join_room(data, user, db)
    
    elif message_type == "leave_room":
        await handle_leave_room(data, user)
    
    elif message_type == "mark_read":
        await handle_mark_read(data, user, db)
    
    else:
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        })


async def handle_send_message(data: dict, user: User, db: AsyncSession):
    """Handle sending a message."""
    try:
        # Validate
        msg_data = WSMessageSend(**data)
        
        # Create message
        service = ChatService(db)
        message_create = MessageCreate(
            room_id=msg_data.room_id,
            content=msg_data.content,
            parent_message_id=msg_data.parent_message_id
        )
        
        await service.send_message(message_create, user)
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise


async def handle_typing(data: dict, user: User):
    """Handle typing indicator."""
    try:
        typing_data = WSTypingIndicator(**data)
        
        await connection_manager.broadcast_typing(
            room_id=typing_data.room_id,
            user_id=user.id,
            username=user.full_name or user.email.split('@')[0],  # Use full_name if available
            is_typing=typing_data.is_typing
        )
    
    except Exception as e:
        logger.error(f"Error handling typing: {e}")


async def handle_join_room(data: dict, user: User, db: AsyncSession):
    """Handle joining a room."""
    try:
        join_data = WSJoinRoom(**data)
        
        # Verify user has access to room
        service = ChatService(db)
        await service.get_room(join_data.room_id, user)
        
        # Subscribe to room
        await connection_manager.subscribe_to_room(user.id, join_data.room_id)
        
        # Notify room
        await connection_manager.broadcast_to_room(
            join_data.room_id,
            {
                "type": "user_joined",
                "room_id": join_data.room_id,
                "user_id": user.id
            },
            exclude_user_id=user.id
        )
    
    except Exception as e:
        logger.error(f"Error joining room: {e}")
        raise


async def handle_leave_room(data: dict, user: User):
    """Handle leaving a room."""
    try:
        leave_data = WSLeaveRoom(**data)
        
        await connection_manager.unsubscribe_from_room(user.id, leave_data.room_id)
        
        # Notify room
        await connection_manager.broadcast_to_room(
            leave_data.room_id,
            {
                "type": "user_left",
                "room_id": leave_data.room_id,
                "user_id": user.id
            }
        )
    
    except Exception as e:
        logger.error(f"Error leaving room: {e}")


async def handle_mark_read(data: dict, user: User, db: AsyncSession):
    """Handle marking messages as read."""
    try:
        read_data = WSMarkRead(**data)
        
        service = ChatService(db)
        await service.mark_as_read(read_data.room_id, read_data.message_id, user)
    
    except Exception as e:
        logger.error(f"Error marking read: {e}")
