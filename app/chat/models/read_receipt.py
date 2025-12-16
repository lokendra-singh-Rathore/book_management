"""
Message read receipt model for tracking message reads.
"""
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MessageReadReceipt(Base):
    """
    Read receipts for messages.
    
    Tracks when users read messages for "seen" functionality.
    """
    
    __tablename__ = "message_read_receipts"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    
    # Foreign keys
    message_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chat_messages.id", ondelete="CASCADE"),
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    
    # Timestamp
    read_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, init=False)
    
    # Relationships
    message: Mapped["ChatMessage"] = relationship(
        "ChatMessage",
        back_populates="read_receipts",
        init=False
    )
    
    user: Mapped["User"] = relationship(
        "User",
        init=False
    )
    
    # Unique constraint: one read receipt per user per message
    __table_args__ = (
        UniqueConstraint('message_id', 'user_id', name='uq_message_user_read'),
    )
    
    def __repr__(self) -> str:
        return f"<MessageReadReceipt(message_id={self.message_id}, user_id={self.user_id})>"
