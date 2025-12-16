"""
Run all Kafka consumers.

This script starts all event consumers to process messages from Kafka topics.
Each consumer runs in its own asyncio task.

Usage:
    python -m scripts.run_consumers
"""
import asyncio
import logging
import signal
import sys

# Add project root to path
sys.path.insert(0, '.')

from app.consumers import (
    EmailConsumer,
    AuditConsumer,
    AnalyticsConsumer,
    NotificationConsumer,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Global flag for graceful shutdown
shutdown_event = asyncio.Event()


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {sig}, initiating graceful shutdown...")
    shutdown_event.set()


async def run_consumer(consumer_class, name: str):
    """
    Run a single consumer with error handling.
    
    Args:
        consumer_class: Consumer class to instantiate
        name: Consumer name for logging
    """
    consumer = consumer_class()
    try:
        logger.info(f"Starting {name}...")
        # Run consumer with automatic retry
        await consumer.run_with_retry(max_retries=3, retry_delay=5)
    except Exception as e:
        logger.error(f"{name} failed: {e}", exc_info=True)


async def main():
    """Run all consumers concurrently."""
    logger.info("="*70)
    logger.info("📦 Starting Kafka Consumers")
    logger.info("="*70)
    
    # Create tasks for all consumers
    tasks = [
        asyncio.create_task(run_consumer(EmailConsumer, "EmailConsumer")),
        asyncio.create_task(run_consumer(AuditConsumer, "AuditConsumer")),
        asyncio.create_task(run_consumer(AnalyticsConsumer, "AnalyticsConsumer")),
        asyncio.create_task(run_consumer(NotificationConsumer, "NotificationConsumer")),
    ]
    
    logger.info(f"✅ Started {len(tasks)} consumers")
    logger.info("Press Ctrl+C to stop all consumers\n")
    
    try:
        # Wait for shutdown signal
        await shutdown_event.wait()
        
        # Cancel all tasks
        logger.info("\n🛑 Stopping all consumers...")
        for task in tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
    except KeyboardInterrupt:
        logger.info("\nKeyboard interrupt received")
    finally:
        logger.info("👋 All consumers stopped")


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Exiting...")
