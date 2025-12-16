"""
Pydantic schemas for chat API.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from app.chat.models.room import RoomType
from app.chat.models.message import MessageType
from app.chat.models.participant import ParticipantRole


# ============ Room Schemas ============

class RoomCreate(BaseModel):
    """Schema for creating a chat room."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    room_type: RoomType
    is_private: bool = False
    participant_ids: Optional[List[int]] = Field(default_factory=list)


class RoomUpdate(BaseModel):
    """Schema for updating a room."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_private: Optional[bool] = None


class ParticipantResponse(BaseModel):
    """Schema for room participant."""
    user_id: int
    role: ParticipantRole
    joined_at: datetime
    is_muted: bool
    
    model_config = {"from_attributes": True}


class RoomResponse(BaseModel):
    """Schema for room response."""
    id: int
    name: str
    description: Optional[str]
    room_type: RoomType
    creator_id: Optional[int]
    is_private: bool
    created_at: datetime
    updated_at: datetime
    participant_count: Optional[int] = None
    unread_count: Optional[int] = None
    
    model_config = {"from_attributes": True}


class RoomDetailResponse(RoomResponse):
    """Detailed room response with participants."""
    participants: List[ParticipantResponse] = []


# ============ Message Schemas ============

class MessageCreate(BaseModel):
    """Schema for creating a message."""
    content: str = Field(..., min_length=1, max_length=5000)  # Max 5000 chars
    room_id: int
    message_type: MessageType = MessageType.TEXT
    parent_message_id: Optional[int] = None
    metadata: Optional[dict] = None


class MessageUpdate(BaseModel):
    """Schema for updating a message."""
    content: str = Field(..., min_length=1, max_length=5000)  # Max 5000 chars


class ReactionCreate(BaseModel):
    """Schema for adding a reaction."""
    emoji: str = Field(..., min_length=1, max_length=10)
    
    @field_validator('emoji')
    @classmethod
    def validate_emoji(cls, v: str) -> str:
        """Ensure emoji is not empty."""
        if not v.strip():
            raise ValueError('Emoji cannot be empty')
        return v.strip()


class ReactionResponse(BaseModel):
    """Schema for reaction response."""
    id: int
    message_id: int
    user_id: int
    emoji: str
    created_at: datetime
    
    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: int
    room_id: int
    sender_id: Optional[int]
    content: str
    message_type: MessageType
    parent_message_id: Optional[int]
    metadata: Optional[dict]
    is_edited: bool
    edited_at: Optional[datetime]
    created_at: datetime
    reactions: List[ReactionResponse] = []
    read_count: Optional[int] = None
    
    model_config = {"from_attributes": True}


class PaginatedMessages(BaseModel):
    """Paginated messages response."""
    messages: List[MessageResponse]
    total: int
    has_more: bool
    next_cursor: Optional[int] = None


# ============ WebSocket Schemas ============

class WSMessageSend(BaseModel):
    """WebSocket message send schema."""
    type: str = "send_message"
    room_id: int
    content: str
    parent_message_id: Optional[int] = None


class WSTypingIndicator(BaseModel):
    """WebSocket typing indicator schema."""
    type: str = "typing"
    room_id: int
    is_typing: bool


class WSJoinRoom(BaseModel):
    """WebSocket join room schema."""
    type: str = "join_room"
    room_id: int


class WSLeaveRoom(BaseModel):
    """WebSocket leave room schema."""
    type: str = "leave_room"
    room_id: int


class WSMarkRead(BaseModel):
    """WebSocket mark messages as read schema."""
    type: str = "mark_read"
    room_id: int
    message_id: int


# ============ Participant Schemas ============

class AddParticipant(BaseModel):
    """Schema for adding participant to room."""
    user_id: int
    role: ParticipantRole = ParticipantRole.MEMBER


class UpdateParticipant(BaseModel):
    """Schema for updating participant."""
    role: Optional[ParticipantRole] = None
    is_muted: Optional[bool] = None


# ============ Statistics Schemas ============

class RoomStats(BaseModel):
    """Room statistics."""
    total_messages: int
    total_participants: int
    online_participants: int
    unread_messages: int


class UserChatStats(BaseModel):
    """User chat statistics."""
    total_rooms: int
    total_unread: int
    active_chats: int
