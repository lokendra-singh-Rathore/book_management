"""
Kafka producer for publishing events.
Uses singleton pattern to maintain single producer instance.
"""
import logging
import msgpack
from typing import Optional, Any, Dict
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from app.config import settings


logger = logging.getLogger(__name__)


class KafkaProducer:
    """
    Singleton Kafka producer for publishing events.
    
    Handles message serialization, batching, and error handling.
    """
    
    _instance: Optional['KafkaProducer'] = None
    _producer: Optional[AIOKafkaProducer] = None
    
    def __new__(cls):
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def start(self):
        """Initialize and start the Kafka producer."""
        if self._producer is not None:
            logger.warning("Kafka producer already started")
            return
        
        if not settings.KAFKA_ENABLE:
            logger.info("Kafka is disabled in configuration")
            return
        
        try:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers_list,
                value_serializer=lambda v: msgpack.packb(v, use_bin_type=True),
                compression_type=settings.KAFKA_COMPRESSION_TYPE,
                max_batch_size=16384,
                linger_ms=10,  # Wait 10ms to batch messages for better throughput
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,
            )
            await self._producer.start()
            logger.info(
                f"✅ Kafka producer started - Servers: {settings.KAFKA_BOOTSTRAP_SERVERS}"
            )
        except Exception as e:
            logger.error(f"❌ Failed to start Kafka producer: {e}")
            self._producer = None
    
    async def stop(self):
        """Stop the producer gracefully."""
        if self._producer:
            try:
                await self._producer.stop()
                logger.info("Kafka producer stopped")
            except Exception as e:
                logger.error(f"Error stopping Kafka producer: {e}")
            finally:
                self._producer = None
    
    async def send_event(
        self, 
        topic: str, 
        event: Dict[str, Any], 
        key: Optional[str] = None
    ) -> bool:
        """
        Send an event to a Kafka topic.
        
        Args:
            topic: Kafka topic name
            event: Event data (will be serialized to msgpack)
            key: Optional partition key for message ordering
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not settings.KAFKA_ENABLE:
            logger.debug(f"Kafka disabled - Event not sent: {event.get('event_type')}")
            return False
        
        if self._producer is None:
            logger.error("Kafka producer not initialized")
            return False
        
        try:
            # Send event
            key_bytes = key.encode('utf-8') if key else None
            
            await self._producer.send_and_wait(
                topic=topic,
                value=event,
                key=key_bytes
            )
            
            logger.info(
                f"📤 Event sent to '{topic}': {event.get('event_type')} "
                f"(ID: {event.get('event_id', 'N/A')[:8]}...)"
            )
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error sending event to {topic}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending event to {topic}: {e}")
            return False
    
    async def send_batch(self, topic: str, events: list[Dict[str, Any]]) -> int:
        """
        Send multiple events in batch.
        
        Args:
            topic: Kafka topic name
            events: List of event dictionaries
        
        Returns:
            int: Number of successfully sent events
        """
        if not settings.KAFKA_ENABLE or self._producer is None:
            return 0
        
        success_count = 0
        for event in events:
            if await self.send_event(topic, event):
                success_count += 1
        
        return success_count


# Global producer instance
kafka_producer = KafkaProducer()
