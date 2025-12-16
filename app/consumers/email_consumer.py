"""
Email notification consumer.
Processes events and sends email notifications (simulated).
"""
import asyncio
import logging

from app.events.consumer import BaseKafkaConsumer
from app.events.topics import KafkaTopics
from app.events.schemas import EventType
from app.config import settings


logger = logging.getLogger(__name__)


class EmailConsumer(BaseKafkaConsumer):
    """
    Consumer for sending email notifications based on events.
    
    In production, integrate with SendGrid, AWS SES, or similar service.
    """
    
    def __init__(self):
        super().__init__(
            topics=[KafkaTopics.BOOK_EVENTS, KafkaTopics.USER_EVENTS],
            group_id=settings.KAFKA_GROUP_EMAIL
        )
    
    async def process_message(self, event: dict):
        """Process event and send appropriate email."""
        event_type = event.get("event_type")
        
        if event_type == EventType.BOOK_SHARED:
            await self._send_book_shared_email(event)
        elif event_type == EventType.USER_REGISTERED:
            await self._send_welcome_email(event)
        elif event_type == EventType.BOOK_CREATED:
            await self._send_book_created_notification(event)
    
    async def _send_book_shared_email(self, event: dict):
        """Send email when a book is shared."""
        self.logger.info(
            f"📧 Email: Book '{event.get('title')}' shared with "
            f"{event.get('shared_with_email')} by user {event.get('user_id')}"
        )
        
        # Simulate email sending delay
        await asyncio.sleep(0.1)
        
        # In production:
        # await send_email(
        #     to=event.get('shared_with_email'),
        #     subject=f"Book Shared: {event.get('title')}",
        #     template='book_shared',
        #     context={'title': event.get('title'), 'author': event.get('author')}
        # )
    
    async def _send_welcome_email(self, event: dict):
        """Send welcome email to newly registered user."""
        self.logger.info(
            f"📧 Welcome email sent to {event.get('email')} "
            f"(User ID: {event.get('user_id')})"
        )
        
        await asyncio.sleep(0.1)
        
        # In production:
        # await send_email(
        #     to=event.get('email'),
        #     subject='Welcome to Book Management API!',
        #     template='welcome',
        #     context={'full_name': event.get('full_name')}
        # )
    
    async def _send_book_created_notification(self, event: dict):
        """Optionally notify user when they create a book."""
        self.logger.info(
            f"📧 Book creation confirmation for '{event.get('title')}' "
            f"to user {event.get('user_id')}"
        )
        
        await asyncio.sleep(0.1)
