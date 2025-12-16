"""
Kafka consumers package.
Contains all event consumers.
"""
from app.consumers.email_consumer import EmailConsumer
from app.consumers.audit_consumer import AuditConsumer
from app.consumers.analytics_consumer import AnalyticsConsumer
from app.consumers.notification_consumer import NotificationConsumer

__all__ = [
    "EmailConsumer",
    "AuditConsumer",
    "AnalyticsConsumer",
    "NotificationConsumer",
]
