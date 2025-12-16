"""
Event service for orchestrating Kafka event publishing.
Provides high-level methods for publishing domain events.
"""
import logging
from typing import Optional, Dict, Any

from app.events.producer import kafka_producer
from app.events.topics import KafkaTopics
from app.events.schemas import (
    BookEvent,
    UserEvent,
    NotificationEvent,
    AuditLogEvent,
    EventType,
)


logger = logging.getLogger(__name__)


class EventService:
    """
    Service for publishing events to Kafka.
    
    Provides domain-specific methods for publishing events with proper schema validation.
    """
    
    @staticmethod
    async def publish_book_created(
        book_id: int,
        title: str,
        author: str,
        isbn: Optional[str],
        user_id: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Publish book created event."""
        event = BookEvent(
            event_type=EventType.BOOK_CREATED,
            book_id=book_id,
            title=title,
            author=author,
            isbn=isbn,
            action="created",
            user_id=user_id,
            metadata=metadata or {}
        )
        
        return await kafka_producer.send_event(
            topic=KafkaTopics.BOOK_EVENTS,
            event=event.model_dump(mode='json'),
            key=str(book_id)  # Same book events go to same partition
        )
    
    @staticmethod
    async def publish_book_updated(
        book_id: int,
        title: str,
        author: str,
        isbn: Optional[str],
        user_id: int,
        changes: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Publish book updated event."""
        event = BookEvent(
            event_type=EventType.BOOK_UPDATED,
            book_id=book_id,
            title=title,
            author=author,
            isbn=isbn,
            action="updated",
            user_id=user_id,
            metadata={"changes": changes} if changes else {}
        )
        
        return await kafka_producer.send_event(
            topic=KafkaTopics.BOOK_EVENTS,
            event=event.model_dump(mode='json'),
            key=str(book_id)
        )
    
    @staticmethod
    async def publish_book_deleted(
        book_id: int,
        title: str,
        author: str,
        user_id: int
    ) -> bool:
        """Publish book deleted event."""
        event = BookEvent(
            event_type=EventType.BOOK_DELETED,
            book_id=book_id,
            title=title,
            author=author,
            action="deleted",
            user_id=user_id
        )
        
        return await kafka_producer.send_event(
            topic=KafkaTopics.BOOK_EVENTS,
            event=event.model_dump(mode='json'),
            key=str(book_id)
        )
    
    @staticmethod
    async def publish_book_shared(
        book_id: int,
        title: str,
        author: str,
        owner_user_id: int,
        shared_with_user_id: int,
        shared_with_email: str
    ) -> bool:
        """Publish book shared event."""
        event = BookEvent(
            event_type=EventType.BOOK_SHARED,
            book_id=book_id,
            title=title,
            author=author,
            action="shared",
            user_id=owner_user_id,
            shared_with_user_id=shared_with_user_id,
            shared_with_email=shared_with_email
        )
        
        return await kafka_producer.send_event(
            topic=KafkaTopics.BOOK_EVENTS,
            event=event.model_dump(mode='json'),
            key=str(book_id)
        )
    
    @staticmethod
    async def publish_book_unshared(
        book_id: int,
        title: str,
        author: str,
        owner_user_id: int,
        removed_user_id: int
    ) -> bool:
        """Publish book unshared event."""
        event = BookEvent(
            event_type=EventType.BOOK_UNSHARED,
            book_id=book_id,
            title=title,
            author=author,
            action="unshared",
            user_id=owner_user_id,
            shared_with_user_id=removed_user_id
        )
        
        return await kafka_producer.send_event(
            topic=KafkaTopics.BOOK_EVENTS,
            event=event.model_dump(mode='json'),
            key=str(book_id)
        )
    
    @staticmethod
    async def publish_user_registered(
        user_id: int,
        email: str,
        full_name: Optional[str]
    ) -> bool:
        """Publish user registered event."""
        event = UserEvent(
            event_type=EventType.USER_REGISTERED,
            user_id=user_id,
            email=email,
            full_name=full_name,
            action="registered"
        )
        
        return await kafka_producer.send_event(
            topic=KafkaTopics.USER_EVENTS,
            event=event.model_dump(mode='json'),
            key=str(user_id)
        )
    
    @staticmethod
    async def publish_user_login(
        user_id: int,
        email: str
    ) -> bool:
        """Publish user login event."""
        event = UserEvent(
            event_type=EventType.USER_LOGIN,
            user_id=user_id,
            email=email,
            action="login"
        )
        
        return await kafka_producer.send_event(
            topic=KafkaTopics.USER_EVENTS,
            event=event.model_dump(mode='json'),
            key=str(user_id)
        )
    
    @staticmethod
    async def publish_notification(
        recipient_user_id: int,
        title: str,
        message: str,
        notification_type: str = "in_app",
        priority: str = "normal",
        event_id: Optional[str] = None
    ) -> bool:
        """Publish notification event."""
        event = NotificationEvent(
            event_type=EventType.NOTIFICATION_SENT,
            recipient_user_id=recipient_user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            metadata={"source_event_id": event_id} if event_id else {}
        )
        
        return await kafka_producer.send_event(
            topic=KafkaTopics.NOTIFICATIONS,
            event=event.model_dump(mode='json'),
            key=str(recipient_user_id)
        )
    
    @staticmethod
    async def publish_audit_log(
        user_id: Optional[int],
        resource_type: str,
        resource_id: int,
        action: str,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Publish audit log event."""
        event = AuditLogEvent(
            event_type=EventType.AUDIT_LOG,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return await kafka_producer.send_event(
            topic=KafkaTopics.AUDIT_LOG,
            event=event.model_dump(mode='json'),
            key=f"{resource_type}:{resource_id}"
        )


# Global event service instance
event_service = EventService()
