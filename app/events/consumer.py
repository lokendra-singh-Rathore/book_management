"""
Base Kafka consumer using Template Method pattern.
All specific consumers inherit from this base class.
"""
import logging
import asyncio
import msgpack
from abc import ABC, abstractmethod
from typing import Optional, List
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

from app.config import settings


logger = logging.getLogger(__name__)


class BaseKafkaConsumer(ABC):
    """
    Abstract base class for Kafka consumers.
    
    Implements the Template Method pattern - subclasses must implement process_message().
    Handles connection management, error handling, and graceful shutdown.
    """
    
    def __init__(self, topics: List[str], group_id: str):
        """
        Initialize consumer.
        
        Args:
            topics: List of Kafka topics to subscribe to
            group_id: Consumer group ID for load balancing
        """
        self.topics = topics
        self.group_id = group_id
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self._running = False
    
    async def start(self):
        """Start consuming messages from Kafka topics."""
        if not settings.KAFKA_ENABLE:
            self.logger.info(f"Kafka disabled - {self.__class__.__name__} not started")
            return
        
        try:
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=settings.kafka_bootstrap_servers_list,
                group_id=self.group_id,
                value_deserializer=lambda m: msgpack.unpackb(m, raw=False),
                auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
                enable_auto_commit=settings.KAFKA_ENABLE_AUTO_COMMIT,
                max_poll_records=100,
            )
            
            await self.consumer.start()
            self._running = True
            self.logger.info(
                f"✅ Consumer '{self.group_id}' started for topics: {self.topics}"
            )
            
            # Start consuming
            await self._consume_loop()
            
        except Exception as e:
            self.logger.error(f"Failed to start consumer: {e}")
            raise
        finally:
            await self.stop()
    
    async def _consume_loop(self):
        """Main consumption loop."""
        try:
            async for message in self.consumer:
                if not self._running:
                    break
                
                try:
                    event = message.value
                    self.logger.debug(
                        f"📥 Received {event.get('event_type')} from {message.topic}"
                    )
                    
                    # Process message in subclass
                    await self.process_message(event)
                    
                except Exception as e:
                    self.logger.error(
                        f"Error processing message from {message.topic}: {e}",
                        exc_info=True
                    )
                    # Continue processing other messages
                    continue
                    
        except KafkaError as e:
            self.logger.error(f"Kafka error in consume loop: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in consume loop: {e}")
    
    async def stop(self):
        """Stop the consumer gracefully."""
        self._running = False
        if self.consumer:
            try:
                await self.consumer.stop()
                self.logger.info(f"Consumer '{self.group_id}' stopped")
            except Exception as e:
                self.logger.error(f"Error stopping consumer: {e}")
            finally:
                self.consumer = None
    
    @abstractmethod
    async def process_message(self, event: dict):
        """
        Process a single message from Kafka.
        
        Must be implemented by subclasses.
        
        Args:
            event: Deserialized event dictionary
        """
        pass
    
    async def run_with_retry(self, max_retries: int = 3, retry_delay: int = 5):
        """
        Run consumer with automatic retry on failure.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        retries = 0
        while retries < max_retries:
            try:
                await self.start()
                break  # Successfully started
            except Exception as e:
                retries += 1
                self.logger.error(
                    f"Consumer failed (attempt {retries}/{max_retries}): {e}"
                )
                if retries < max_retries:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    self.logger.error("Max retries reached. Consumer stopped.")
