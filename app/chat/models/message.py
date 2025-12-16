"""
Chat message model.
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import String, Integer, Text, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MessageType(str, Enum):
    """Message content types."""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"      # System notifications (user joined, etc.)


class ChatMessage(Base):
    """
    Chat message with rich content support.
    
    Features:
    - Text messages
    - Image/file attachments
    - Message threading (replies)
    - Edit history
    - System messages
    """
    
    __tablename__ = "chat_messages"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    
    # Message details
    room_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chat_rooms.id", ondelete="CASCADE"),
        index=True
    )
    sender_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Content
    content: Mapped[str] = mapped_column(Text)
    message_type: Mapped[MessageType] = mapped_column(
        SQLEnum(MessageType),
        default=MessageType.TEXT
    )
    
    # Threading (reply to message)
    parent_message_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("chat_messages.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Metadata (attachments, mentions, etc.)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=None)
    
    # Edit tracking
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    edited_at: Mapped[Optional[datetime]] = mapped_column(nullable=True, default=None)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        init=False,
        index=True
    )
    
    # Relationships
    room: Mapped["ChatRoom"] = relationship(
        "ChatRoom",
        back_populates="messages",
        init=False
    )
    
    sender: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[sender_id],
        init=False
    )
    
    parent_message: Mapped[Optional["ChatMessage"]] = relationship(
        "ChatMessage",
        remote_side=[id],
        foreign_keys=[parent_message_id],
        init=False
    )
    
    reactions: Mapped[list["MessageReaction"]] = relationship(
        "MessageReaction",
        back_populates="message",
        cascade="all, delete-orphan",
        default_factory=list,
        init=False
    )
    
    read_receipts: Mapped[list["MessageReadReceipt"]] = relationship(
        "MessageReadReceipt",
        back_populates="message",
        cascade="all, delete-orphan",
        default_factory=list,
        init=False
    )
    
    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, room_id={self.room_id}, type={self.message_type})>"
