"""
Chat room model for group chats, direct messages, and channels.
"""
from datetime import datetime
from typing import List, Optional
from enum import Enum
from sqlalchemy import String, Integer, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RoomType(str, Enum):
    """Chat room types."""
    DIRECT = "direct"        # One-on-one conversation
    GROUP = "group"          # Group chat
    CHANNEL = "channel"      # Broadcast channel


class ChatRoom(Base):
    """
    Chat room for conversations.
    
    Supports:
    - Direct messages (2 participants)
    - Group chats (multiple participants)
    - Channels (broadcast to many)
    """
    
    __tablename__ = "chat_rooms"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    
    # Room details
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=None)
    room_type: Mapped[RoomType] = mapped_column(SQLEnum(RoomType))
    
    # Creator
    creator_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Settings
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, init=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        init=False
    )
    
    # Relationships
    participants: Mapped[List["RoomParticipant"]] = relationship(
        "RoomParticipant",
        back_populates="room",
        cascade="all, delete-orphan",
        default_factory=list,
        init=False
    )
    
    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="room",
        cascade="all, delete-orphan",
        default_factory=list,
        init=False
    )
    
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[creator_id],
        init=False
    )
    
    def __repr__(self) -> str:
        return f"<ChatRoom(id={self.id}, name={self.name}, type={self.room_type})>"
