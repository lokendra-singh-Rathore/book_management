"""
Analytics consumer.
Aggregates events for analytics and reporting.
"""
import logging
from collections import defaultdict
from datetime import datetime

from app.events.consumer import BaseKafkaConsumer
from app.events.topics import KafkaTopics
from app.events.schemas import EventType
from app.config import settings


logger = logging.getLogger(__name__)


class AnalyticsConsumer(BaseKafkaConsumer):
    """
    Consumer for analyzing events and generating metrics.
    
    In production, this would write to a data warehouse or analytics database.
    For now, it logs aggregated statistics.
    """
    
    def __init__(self):
        super().__init__(
            topics=[KafkaTopics.BOOK_EVENTS, KafkaTopics.USER_EVENTS],
            group_id=settings.KAFKA_GROUP_ANALYTICS
        )
        
        # In-memory counters (in production, use Redis or database)
        self.stats = {
            'books_created': 0,
            'books_updated': 0,
            'books_deleted': 0,
            'books_shared': 0,
            'users_registered': 0,
            'user_logins': 0,
        }
        
        self.last_report_time = datetime.utcnow()
        self.report_interval_seconds = 60  # Report every 60 seconds
    
    async def process_message(self, event: dict):
        """Process event and update analytics."""
        event_type = event.get('event_type')
        
        # Update counters
        if event_type == EventType.BOOK_CREATED:
            self.stats['books_created'] += 1
        elif event_type == EventType.BOOK_UPDATED:
            self.stats['books_updated'] += 1
        elif event_type == EventType.BOOK_DELETED:
            self.stats['books_deleted'] += 1
        elif event_type == EventType.BOOK_SHARED:
            self.stats['books_shared'] += 1
        elif event_type == EventType.USER_REGISTERED:
            self.stats['users_registered'] += 1
        elif event_type == EventType.USER_LOGIN:
            self.stats['user_logins'] += 1
        
        # Periodically report stats
        await self._maybe_report_stats()
    
    async def _maybe_report_stats(self):
        """Report statistics if interval has passed."""
        now = datetime.utcnow()
        elapsed = (now - self.last_report_time).total_seconds()
        
        if elapsed >= self.report_interval_seconds:
            self._report_stats()
            self.last_report_time = now
    
    def _report_stats(self):
        """Log current statistics."""
        self.logger.info("📊 Analytics Report:")
        self.logger.info(f"  Books Created: {self.stats['books_created']}")
        self.logger.info(f"  Books Updated: {self.stats['books_updated']}")
        self.logger.info(f"  Books Deleted: {self.stats['books_deleted']}")
        self.logger.info(f"  Books Shared: {self.stats['books_shared']}")
        self.logger.info(f"  Users Registered: {self.stats['users_registered']}")
        self.logger.info(f"  User Logins: {self.stats['user_logins']}")
        
        # In production:
        # - Write to data warehouse (Snowflake, BigQuery, Redshift)
        # - Update dashboards (Grafana, Metabase)
        # - Send to analytics platform (Mixpanel, Amplitude)
