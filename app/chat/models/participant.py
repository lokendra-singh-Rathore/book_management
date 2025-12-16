"""
Room participant model for chat room membership.
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import String, Integer, ForeignKey, Boolean, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ParticipantRole(str, Enum):
    """Participant roles in chat rooms."""
    OWNER = "owner"      # Room creator, full permissions
    ADMIN = "admin"      # Can manage members, settings
    MEMBER = "member"    # Regular participant


class RoomParticipant(Base):
    """
    Room membership and participant settings.
    
    Tracks:
    - User's role in the room
    - When they joined
    - Last read message
    - Mute settings
    """
    
    __tablename__ = "room_participants"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    
    # Foreign keys
    room_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chat_rooms.id", ondelete="CASCADE"),
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    
    # Role and permissions
    role: Mapped[ParticipantRole] = mapped_column(
        SQLEnum(ParticipantRole),
        default=ParticipantRole.MEMBER
    )
    
    # Read tracking
    last_read_at: Mapped[Optional[datetime]] = mapped_column(nullable=True, default=None)
    
    # Settings
    is_muted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    joined_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, init=False)
    
    # Relationships
    room: Mapped["ChatRoom"] = relationship(
        "ChatRoom",
        back_populates="participants",
        init=False
    )
    
    user: Mapped["User"] = relationship(
        "User",
        init=False
    )
    
    # Unique constraint: one user can only be in a room once
    __table_args__ = (
        UniqueConstraint('room_id', 'user_id', name='uq_room_participant'),
    )
    
    def __repr__(self) -> str:
        return f"<RoomParticipant(room_id={self.room_id}, user_id={self.user_id}, role={self.role})>"
