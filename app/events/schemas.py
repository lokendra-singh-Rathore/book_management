"""
Event schemas using Pydantic for type safety and validation.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event type enumeration."""
    
    # Book events
    BOOK_CREATED = "book.created"
    BOOK_UPDATED = "book.updated"
    BOOK_DELETED = "book.deleted"
    BOOK_SHARED = "book.shared"
    BOOK_UNSHARED = "book.unshared"
    
    # User events
    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    
    # Notification events
    NOTIFICATION_SENT = "notification.sent"
    
    # Audit events
    AUDIT_LOG = "audit.log"


class BaseEvent(BaseModel):
    """Base event schema with common fields."""
    
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BookEvent(BaseEvent):
    """Book-related events."""
    
    book_id: int
    title: str
    author: str
    isbn: Optional[str] = None
    action: str  # created, updated, deleted, shared
    
    # For shared events
    shared_with_user_id: Optional[int] = None
    shared_with_email: Optional[str] = None


class UserEvent(BaseEvent):
    """User-related events."""
    
    email: str
    full_name: Optional[str] = None
    action: str  # registered, login, logout


class NotificationEvent(BaseEvent):
    """Notification events."""
    
    recipient_user_id: int
    title: str
    message: str
    notification_type: str  # email, push, in_app
    priority: str = "normal"  # low, normal, high


class AuditLogEvent(BaseEvent):
    """Audit log events."""
    
    resource_type: str  # book, user
    resource_id: int
    action: str  # create, read, update, delete
    changes: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
