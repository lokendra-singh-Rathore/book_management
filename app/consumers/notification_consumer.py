"""
Notification consumer.
Creates in-app notifications stored in database.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.events.consumer import BaseKafkaConsumer
from app.events.topics import KafkaTopics
from app.core.database import async_session_maker
from app.models.notification import Notification
from app.events.schemas import EventType
from app.config import settings


logger = logging.getLogger(__name__)


class NotificationConsumer(BaseKafkaConsumer):
    """
    Consumer for creating in-app notifications.
    
    Stores notifications in database for users to view in their dashboard.
    """
    
    def __init__(self):
        super().__init__(
            topics=[KafkaTopics.BOOK_EVENTS, KafkaTopics.NOTIFICATIONS],
            group_id=settings.KAFKA_GROUP_NOTIFICATION
        )
    
    async def process_message(self, event: dict):
        """Process event and create notification if needed."""
        event_type = event.get('event_type')
        
        if event_type == EventType.BOOK_SHARED:
            await self._create_book_shared_notification(event)
        elif event_type == EventType.NOTIFICATION_SENT:
            await self._create_generic_notification(event)
    
    async def _create_book_shared_notification(self, event: dict):
        """Create notification when book is shared with user."""
        shared_with_user_id = event.get('shared_with_user_id')
        
        if not shared_with_user_id:
            return
        
        try:
            async with async_session_maker() as session:
                notification = Notification(
                    user_id=shared_with_user_id,
                    title="📚 Book Shared With You",
                    message=f"{event.get('title')} by {event.get('author')} has been shared with you!",
                    notification_type="in_app",
                    priority="normal",
                    event_id=event.get('event_id')
                )
                
                session.add(notification)
                await session.commit()
                
                self.logger.info(
                    f"🔔 Notification created for user {shared_with_user_id}: "
                    f"Book '{event.get('title')}' shared"
                )
        except Exception as e:
            self.logger.error(f"Failed to create notification: {e}", exc_info=True)
    
    async def _create_generic_notification(self, event: dict):
        """Create generic notification from notification event."""
        try:
            async with async_session_maker() as session:
                notification = Notification(
                    user_id=event.get('recipient_user_id'),
                    title=event.get('title'),
                    message=event.get('message'),
                    notification_type=event.get('notification_type', 'in_app'),
                    priority=event.get('priority', 'normal'),
                    event_id=event.get('event_id')
                )
                
                session.add(notification)
                await session.commit()
                
                self.logger.info(
                    f"🔔 Notification created for user {event.get('recipient_user_id')}"
                )
        except Exception as e:
            self.logger.error(f"Failed to create notification: {e}", exc_info=True)
