"""
Chat service for business logic and Kafka integration.
"""
import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.chat.models import (
    ChatRoom, ChatMessage, RoomParticipant, MessageReaction, MessageReadReceipt,
    RoomType, MessageType, ParticipantRole
)
from app.chat.schemas import (
    RoomCreate, RoomUpdate, MessageCreate, MessageUpdate,
    RoomResponse, MessageResponse, PaginatedMessages
)
from app.chat.redis_client import redis_client
from app.chat.connection_manager import connection_manager
from app.models.user import User
from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.services.event_service import event_service


logger = logging.getLogger(__name__)


class ChatService:
    """Service for chat operations with Redis caching and Kafka events."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============ Room Management ============
    
    async def create_room(
        self,
        room_data: RoomCreate,
        creator: User
    ) -> ChatRoom:
        """
        Create a chat room.
        
        Args:
            room_data: Room creation data
            creator: User creating the room
        
        Returns:
            Created room instance
        """
        # Create room
        room = ChatRoom(
            name=room_data.name,
            description=room_data.description,
            room_type=room_data.room_type,
            creator_id=creator.id,
            is_private=room_data.is_private
        )
        
        self.db.add(room)
        await self.db.flush()  # Get room ID
        
        # Add creator as owner
        creator_participant = RoomParticipant(
            room_id=room.id,
            user_id=creator.id,
            role=ParticipantRole.OWNER
        )
        self.db.add(creator_participant)
        
        # Add other participants if provided
        if room_data.participant_ids:
            for user_id in room_data.participant_ids:
                if user_id != creator.id:  # Don't duplicate creator
                    participant = RoomParticipant(
                        room_id=room.id,
                        user_id=user_id,
                        role=ParticipantRole.MEMBER
                    )
                    self.db.add(participant)
        
        await self.db.commit()
        await self.db.refresh(room)
        
        # Publish event
        await event_service.publish_notification(
            recipient_user_id=creator.id,
            title="Room Created",
            message=f"Chat room '{room.name}' created successfully",
            notification_type="chat"
        )
        
        logger.info(f"Created room {room.id}: {room.name} by user {creator.id}")
        return room
    
    async def get_room(self, room_id: int, user: User) -> ChatRoom:
        """Get room and verify user access."""
        stmt = select(ChatRoom).where(ChatRoom.id == room_id)
        result = await self.db.execute(stmt)
        room = result.scalar_one_or_none()
        
        if not room:
            raise NotFoundError(detail="Room not found")
        
        # Check if user is participant
        if not await self._is_participant(room_id, user.id):
            raise ForbiddenError(detail="You don't have access to this room")
        
        return room
    
    async def get_user_rooms(self, user: User) -> List[RoomResponse]:
        """Get all rooms user is part of."""
        stmt = (
            select(ChatRoom)
            .join(RoomParticipant)
            .where(RoomParticipant.user_id == user.id)
            .order_by(ChatRoom.updated_at.desc())
        )
        
        result = await self.db.execute(stmt)
        rooms = result.scalars().all()
        
        #Get unread counts from Redis
        unread_counts = await redis_client.get_all_unread_counts(user.id)
        
        # Build responses
        room_responses = []
        for room in rooms:
            room_response = RoomResponse.model_validate(room)
            room_response.unread_count = unread_counts.get(room.id, 0)
            room_responses.append(room_response)
        
        return room_responses
    
    async def update_room(
        self,
        room_id: int,
        room_data: RoomUpdate,
        user: User
    ) -> ChatRoom:
        """Update room (admin/owner only)."""
        room = await self.get_room(room_id, user)
        
        # Check if user is admin or owner
        if not await self._is_admin(room_id, user.id):
            raise ForbiddenError(detail="Only admins can update room")
        
        # Update fields
        update_data = room_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(room, field, value)
        
        room.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(room)
        
        return room
    
    async def delete_room(self, room_id: int, user: User):
        """Delete room (owner only)."""
        room = await self.get_room(room_id, user)
        
        # Only owner can delete
        if room.creator_id != user.id:
            raise ForbiddenError(detail="Only room owner can delete")
        
        await self.db.delete(room)
        await self.db.commit()
        
        logger.info(f"Deleted room {room_id} by user {user.id}")
    
    # ============ Message Management ============
    
    async def send_message(
        self,
        message_data: MessageCreate,
        sender: User
    ) -> MessageResponse:
        """
        Send a message to a room.
        
        This creates the message in DB, caches in Redis, and publishes to Kafka.
        """
        # Verify room access
        await self.get_room(message_data.room_id, sender)
        
        # Create message
        message = ChatMessage(
            room_id=message_data.room_id,
            sender_id=sender.id,
            content=message_data.content,
            message_type=message_data.message_type,
            parent_message_id=message_data.parent_message_id,
            metadata=message_data.metadata
        )
        
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        
        # Build response
        message_dict = {
            "id": message.id,
            "room_id": message.room_id,
            "sender_id": message.sender_id,
            "content": message.content,
            "message_type": message.message_type.value,
            "parent_message_id": message.parent_message_id,
            "metadata": message.metadata,
            "is_edited": message.is_edited,
            "edited_at": message.edited_at.isoformat() if message.edited_at else None,
            "created_at": message.created_at.isoformat(),
            "reactions": [],
            "read_count": 0
        }
        
        # Cache in Redis
        await redis_client.cache_message(message.room_id, message_dict)
        
        # Broadcast via WebSocket
        await connection_manager.broadcast_to_room(
            message.room_id,
            {
                "type": "new_message",
                "message": message_dict
            },
            exclude_user_id=sender.id
        )
        
        # Increment unread counts for other participants
        participants = await self._get_room_participant_ids(message.room_id)
        for participant_id in participants:
            if participant_id != sender.id:
                await redis_client.increment_unread(participant_id, message.room_id)
        
        logger.info(f"Message {message.id} sent to room {message.room_id}")
        
        return MessageResponse.model_validate(message)
    
    async def get_messages(
        self,
        room_id: int,
        user: User,
        limit: int = 50,
        before_id: Optional[int] = None
    ) -> PaginatedMessages:
        """
        Get messages for a room with pagination.
        
        Tries Redis cache first, falls back to PostgreSQL.
        """
        # Verify room access
        await self.get_room(room_id, user)
        
        # Try Redis cache for recent messages
        if not before_id:
            cached_messages = await redis_client.get_cached_messages(
                room_id,
                limit=limit
            )
            
            if cached_messages:
                return PaginatedMessages(
                    messages=[MessageResponse(**msg) for msg in cached_messages],
                    total=len(cached_messages),
                    has_more=len(cached_messages) == limit,
                    next_cursor=cached_messages[-1]["id"] if cached_messages else None
                )
        
        # Fallback to PostgreSQL
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.room_id == room_id)
            .options(
                selectinload(ChatMessage.reactions),
                selectinload(ChatMessage.read_receipts)
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        
        if before_id:
            # Get message timestamp for pagination
            before_stmt = select(ChatMessage.created_at).where(ChatMessage.id == before_id)
            before_result = await self.db.execute(before_stmt)
            before_timestamp = before_result.scalar_one_or_none()
            
            if before_timestamp:
                stmt = stmt.where(ChatMessage.created_at < before_timestamp)
        
        result = await self.db.execute(stmt)
        messages = list(result.scalars().all())
        
        # Get total count
        count_stmt = select(func.count()).select_from(ChatMessage).where(
            ChatMessage.room_id == room_id
        )
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()
        
        return PaginatedMessages(
            messages=[MessageResponse.model_validate(msg) for msg in messages],
            total=total,
            has_more=len(messages) == limit,
            next_cursor=messages[-1].id if messages else None
        )
    
    async def update_message(
        self,
        message_id: int,
        message_data: MessageUpdate,
        user: User
    ) -> MessageResponse:
        """Update message (sender only)."""
        stmt = select(ChatMessage).where(ChatMessage.id == message_id)
        result = await self.db.execute(stmt)
        message = result.scalar_one_or_none()
        
        if not message:
            raise NotFoundError(detail="Message not found")
        
        if message.sender_id != user.id:
            raise ForbiddenError(detail="You can only edit your own messages")
        
        # Update message
        message.content = message_data.content
        message.is_edited = True
        message.edited_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(message)
        
        # Broadcast update
        await connection_manager.broadcast_to_room(
            message.room_id,
            {
                "type": "message_updated",
                "message": MessageResponse.model_validate(message).model_dump(mode='json')
            }
        )
        
        return MessageResponse.model_validate(message)
    
    async def delete_message(self, message_id: int, user: User):
        """Delete message (sender or admin)."""
        stmt = select(ChatMessage).where(ChatMessage.id == message_id)
        result = await self.db.execute(stmt)
        message = result.scalar_one_or_none()
        
        if not message:
            raise NotFoundError(detail="Message not found")
        
        # Check permissions
        is_sender = message.sender_id == user.id
        is_admin = await self._is_admin(message.room_id, user.id)
        
        if not (is_sender or is_admin):
            raise ForbiddenError(detail="No permission to delete this message")
        
        room_id = message.room_id
        
        await self.db.delete(message)
        await self.db.commit()
        
        # Broadcast deletion
        await connection_manager.broadcast_to_room(
            room_id,
            {
                "type": "message_deleted",
                "message_id": message_id
            }
        )
    
    async def mark_as_read(self, room_id: int, message_id: int, user: User):
        """Mark message as read and update last_read_at."""
        # Verify room access
        await self.get_room(room_id, user)
        
        # Create read receipt
        read_receipt = MessageReadReceipt(
            message_id=message_id,
            user_id=user.id
        )
        
        try:
            self.db.add(read_receipt)
            await self.db.commit()
        except:
            # Already read, ignore
            await self.db.rollback()
        
        # Update participant's last_read_at
        stmt = (
            select(RoomParticipant)
            .where(
                and_(
                    RoomParticipant.room_id == room_id,
                    RoomParticipant.user_id == user.id
                )
            )
        )
        result = await self.db.execute(stmt)
        participant = result.scalar_one_or_none()
        
        if participant:
            participant.last_read_at = datetime.utcnow()
            await self.db.commit()
        
        # Reset unread count in Redis
        await redis_client.reset_unread(user.id, room_id)
    
    # ============ Helper Methods ============
    
    async def _is_participant(self, room_id: int, user_id: int) -> bool:
        """Check if user is participant in room."""
        stmt = select(func.count()).select_from(RoomParticipant).where(
            and_(
                RoomParticipant.room_id == room_id,
                RoomParticipant.user_id == user_id
            )
        )
        result = await self.db.execute(stmt)
        count = result.scalar()
        return count > 0
    
    async def _is_admin(self, room_id: int, user_id: int) -> bool:
        """Check if user is admin or owner in room."""
        stmt = select(RoomParticipant.role).where(
            and_(
                RoomParticipant.room_id == room_id,
                RoomParticipant.user_id == user_id
            )
        )
        result = await self.db.execute(stmt)
        role = result.scalar_one_or_none()
        
        return role in [ParticipantRole.ADMIN, ParticipantRole.OWNER]
    
    async def _get_room_participant_ids(self, room_id: int) -> List[int]:
        """Get all participant user IDs for a room."""
        stmt = select(RoomParticipant.user_id).where(
            RoomParticipant.room_id == room_id
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
