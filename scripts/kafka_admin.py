"""
Kafka administrative utilities.

Creates topics, manages offsets, and performs admin tasks.

Usage:
    python -m scripts.kafka_admin create_topics
    python -m scripts.kafka_admin list_topics
    python -m scripts.kafka_admin delete_topics
"""
import asyncio
import sys
import logging
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import TopicAlreadyExistsError

# Add project root to path
sys.path.insert(0, '.')

from app.config import settings
from app.events.topics import KafkaTopics, TopicConfig


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_topics():
    """Create all required Kafka topics."""
    logger.info("Creating Kafka topics...")
    
    admin_client = AIOKafkaAdminClient(
        bootstrap_servers=settings.kafka_bootstrap_servers_list
    )
    
   try:
        await admin_client.start()
        
        # Prepare topics
        new_topics = []
        for topic_name, config in TopicConfig.TOPICS.items():
            new_topic = NewTopic(
                name=topic_name,
                num_partitions=config["num_partitions"],
                replication_factor=config["replication_factor"],
            )
            new_topics.append(new_topic)
        
        # Create topics
        try:
            await admin_client.create_topics(new_topics, validate_only=False)
            logger.info(f"✅ Created {len(new_topics)} topics successfully")
            for topic in new_topics:
                logger.info(f"   - {topic.name} (partitions: {topic.num_partitions})")
        except TopicAlreadyExistsError:
            logger.warning("⚠️ Some or all topics already exist")
        
    except Exception as e:
        logger.error(f"Failed to create topics: {e}")
        raise
    finally:
        await admin_client.close()


async def list_topics():
    """List all Kafka topics."""
    logger.info("Listing Kafka topics...")
    
    admin_client = AIOKafkaAdminClient(
        bootstrap_servers=settings.kafka_bootstrap_servers_list
    )
    
    try:
        await admin_client.start()
        
        metadata = await admin_client.list_topics()
        topics = metadata.topics
        
        logger.info(f"\n📋 Found {len(topics)} topics:")
        for topic in sorted(topics):
            logger.info(f"   - {topic}")
        
    except Exception as e:
        logger.error(f"Failed to list topics: {e}")
        raise
    finally:
        await admin_client.close()


async def delete_topics():
    """Delete all application topics."""
    logger.info("⚠️  WARNING: This will delete all application topics!")
    response = input("Are you sure? (yes/no): ")
    
    if response.lower() != 'yes':
        logger.info("Cancelled")
        return
    
    admin_client = AIOKafkaAdminClient(
        bootstrap_servers=settings.kafka_bootstrap_servers_list
    )
    
    try:
        await admin_client.start()
        
        topics_to_delete = list(TopicConfig.TOPICS.keys())
        
        await admin_client.delete_topics(topics_to_delete)
        logger.info(f"✅ Deleted {len(topics_to_delete)} topics")
        for topic in topics_to_delete:
            logger.info(f"   - {topic}")
        
    except Exception as e:
        logger.error(f"Failed to delete topics: {e}")
        raise
    finally:
        await admin_client.close()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.kafka_admin <command>")
        print("\nCommands:")
        print("  create_topics  - Create all application topics")
        print("  list_topics    - List all topics")
        print("  delete_topics  - Delete all application topics")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create_topics":
        asyncio.run(create_topics())
    elif command == "list_topics":
        asyncio.run(list_topics())
    elif command == "delete_topics":
        asyncio.run(delete_topics())
    else:
        logger.error(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
