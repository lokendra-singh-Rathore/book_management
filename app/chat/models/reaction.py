"""
Message reaction model for emoji reactions.
"""
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MessageReaction(Base):
    """
    Emoji reactions to messages.
    
    Users can react to messages with emojis.
    Each user can only react once per emoji per message.
    """
    
    __tablename__ = "message_reactions"
    
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
    
    # Reaction
    emoji: Mapped[str] = mapped_column(String(50))  # e.g., "👍", "❤️", "😂"
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, init=False)
    
    # Relationships
    message: Mapped["ChatMessage"] = relationship(
        "ChatMessage",
        back_populates="reactions",
        init=False
    )
    
    user: Mapped["User"] = relationship(
        "User",
        init=False
    )
    
    # Unique constraint: one user can only react once with same emoji per message
    __table_args__ = (
        UniqueConstraint('message_id', 'user_id', 'emoji', name='uq_message_user_emoji'),
    )
    
    def __repr__(self) -> str:
        return f"<MessageReaction(message_id={self.message_id}, user_id={self.user_id}, emoji={self.emoji})>"
