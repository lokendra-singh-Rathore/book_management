"""
Test Kafka producer by sending sample events.

This script sends test events to verify Kafka connectivity and event publishing.

Usage:
    python -m scripts.test_producer
"""
import asyncio
import sys
import logging

# Add project root to path
sys.path.insert(0, '.')

from app.services.event_service import event_service
from app.events.producer import kafka_producer


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_book_events():
    """Test book event publishing."""
    logger.info("\n📚 Testing Book Events...")
    
    # Test book created
    success = await event_service.publish_book_created(
        book_id=999,
        title="Test Book: Kafka for Beginners",
        author="John Doe",
        isbn="978-1234567890",
        user_id=1
    )
    logger.info(f"Book Created Event: {'✅ Sent' if success else '❌ Failed'}")
    
    await asyncio.sleep(0.5)
    
    # Test book shared
    success = await event_service.publish_book_shared(
        book_id=999,
        title="Test Book: Kafka for Beginners",
        author="John Doe",
        owner_user_id=1,
        shared_with_user_id=2,
        shared_with_email="test@example.com"
    )
    logger.info(f"Book Shared Event: {'✅ Sent' if success else '❌ Failed'}")


async def test_user_events():
    """Test user event publishing."""
    logger.info("\n👤 Testing User Events...")
    
    # Test user registered
    success = await event_service.publish_user_registered(
        user_id=999,
        email="testuser@example.com",
        full_name="Test User"
    )
    logger.info(f"User Registered Event: {'✅ Sent' if success else '❌ Failed'}")
    
    await asyncio.sleep(0.5)
    
    # Test user login
    success = await event_service.publish_user_login(
        user_id=999,
        email="testuser@example.com"
    )
    logger.info(f"User Login Event: {'✅ Sent' if success else '❌ Failed'}")


async def test_notification_events():
    """Test notification event publishing."""
    logger.info("\n🔔 Testing Notification Events...")
    
    success = await event_service.publish_notification(
        recipient_user_id=1,
        title="Test Notification",
        message="This is a test notification from Kafka",
        notification_type="in_app",
        priority="normal"
    )
    logger.info(f"Notification Event: {'✅ Sent' if success else '❌ Failed'}")


async def test_audit_events():
    """Test audit log event publishing."""
    logger.info("\n📝 Testing Audit Events...")
    
    success = await event_service.publish_audit_log(
        user_id=1,
        resource_type="book",
        resource_id=999,
        action="create",
        changes={"title": "Test Book"},
        ip_address="127.0.0.1"
    )
    logger.info(f"Audit Log Event: {'✅ Sent' if success else '❌ Failed'}")


async def main():
    """Run all tests."""
    logger.info("="*70)
    logger.info("🧪 Kafka Producer Test Suite")
    logger.info("="*70)
    
    try:
        # Start producer
        logger.info("\n🚀 Starting Kafka producer...")
        await kafka_producer.start()
        logger.info("✅ Producer started\n")
        
        # Run tests
        await test_book_events()
        await test_user_events()
        await test_notification_events()
        await test_audit_events()
        
        logger.info("\n" + "="*70)
        logger.info("✅ All tests completed!")
        logger.info("="*70)
        logger.info("\nCheck the consumer logs to verify event processing")
        
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}", exc_info=True)
    finally:
        # Stop producer
        await kafka_producer.stop()
        logger.info("\n👋 Producer stopped")


if __name__ == "__main__":
    asyncio.run(main())
