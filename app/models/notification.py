"""
Notification model for user notifications.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Notification(Base):
    """User notifications for real-time updates."""
    
    __tablename__ = "notifications"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    
    # Recipient
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    
    # Notification content
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    notification_type: Mapped[str] = mapped_column(String(50))  # email, push, in_app
    priority: Mapped[str] = mapped_column(String(20), default="normal")  # low, normal, high
    
    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(nullable=True, default=None)
    
    # Event reference
    event_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        init=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications", init=False)
    
    def __repr__(self) -> str:
        return (
            f"<Notification(id={self.id}, user_id={self.user_id}, "
            f"type={self.notification_type}, read={self.is_read})>"
        )
