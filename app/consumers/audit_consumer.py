"""
Audit log consumer.
Stores all events in the audit_log table for compliance and tracking.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.events.consumer import BaseKafkaConsumer
from app.events.topics import KafkaTopics
from app.core.database import async_session_maker
from app.models.audit_log import AuditLog
from app.config import settings


logger = logging.getLogger(__name__)


class AuditConsumer(BaseKafkaConsumer):
    """
    Consumer for storing audit logs in database.
    
    Captures all events for compliance, debugging, and analytics.
    """
    
    def __init__(self):
        super().__init__(
            topics=[
                KafkaTopics.BOOK_EVENTS,
                KafkaTopics.USER_EVENTS,
                KafkaTopics.AUDIT_LOG
            ],
            group_id=settings.KAFKA_GROUP_AUDIT
        )
    
    async def process_message(self, event: dict):
        """Store event in audit log table."""
        try:
            async with async_session_maker() as session:
                await self._save_audit_log(session, event)
                await session.commit()
                
                self.logger.info(
                    f"📝 Audit log saved: {event.get('event_type')} "
                    f"(Event ID: {event.get('event_id', 'N/A')[:8]}...)"
                )
        except Exception as e:
            self.logger.error(f"Failed to save audit log: {e}", exc_info=True)
    
    async def _save_audit_log(self, session: AsyncSession, event: dict):
        """Save audit log to database."""
        # Extract resource information from event
        resource_type, resource_id = self._extract_resource_info(event)
        
        audit_log = AuditLog(
            event_id=event.get('event_id'),
            event_type=event.get('event_type'),
            user_id=event.get('user_id'),
            resource_type=resource_type,
            resource_id=resource_id,
            action=event.get('action', 'unknown'),
            changes=event.get('changes'),
            metadata=event.get('metadata', {}),
            ip_address=event.get('ip_address'),
            user_agent=event.get('user_agent')
        )
        
        session.add(audit_log)
    
    def _extract_resource_info(self, event: dict) -> tuple[str, int]:
        """Extract resource type and ID from event."""
        event_type = event.get('event_type', '')
        
        if 'book' in event_type:
            return 'book', event.get('book_id', 0)
        elif 'user' in event_type:
            return 'user', event.get('user_id', 0)
        else:
            return 'unknown', 0
