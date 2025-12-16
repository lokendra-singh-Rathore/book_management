"""
Kafka topic definitions and configurations.
"""
from app.config import settings


class KafkaTopics:
    """Centralized Kafka topic names."""
    
    BOOK_EVENTS = settings.KAFKA_TOPIC_BOOK_EVENTS
    USER_EVENTS = settings.KAFKA_TOPIC_USER_EVENTS
    NOTIFICATIONS = settings.KAFKA_TOPIC_NOTIFICATIONS
    AUDIT_LOG = settings.KAFKA_TOPIC_AUDIT_LOG


class TopicConfig:
    """Kafka topic configuration."""
    
    # Topic configurations for creation
    TOPICS = {
        KafkaTopics.BOOK_EVENTS: {
            "num_partitions": 3,
            "replication_factor": 1,
            "retention_ms": 604800000,  # 7 days
        },
        KafkaTopics.USER_EVENTS: {
            "num_partitions": 2,
            "replication_factor": 1,
            "retention_ms": 2592000000,  # 30 days
        },
        KafkaTopics.NOTIFICATIONS: {
            "num_partitions": 2,
            "replication_factor": 1,
            "retention_ms": 86400000,  # 1 day
        },
        KafkaTopics.AUDIT_LOG: {
            "num_partitions": 1,
            "replication_factor": 1,
            "retention_ms": 7776000000,  # 90 days
        },
    }
