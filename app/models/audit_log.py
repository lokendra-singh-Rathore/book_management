"""
Audit log model for tracking all user activities.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditLog(Base):
    """Audit log for tracking all user activities and system events."""
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    
    # Event information
    event_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    
    # User information
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    
    # Resource information
    resource_type: Mapped[str] = mapped_column(String(50))  # book, user
    resource_id: Mapped[int] = mapped_column(Integer)
    action: Mapped[str] = mapped_column(String(50))  # create, read, update, delete
    
    # Details
    changes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=None)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=None)
    
    # Request information
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        init=False
    )
    
    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, event_type={self.event_type}, "
            f"action={self.action}, user_id={self.user_id})>"
        )
