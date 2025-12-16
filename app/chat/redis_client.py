"""
Redis client for chat caching and real-time features.
"""
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import redis.asyncio as redis

from app.config import settings


logger = logging.getLogger(__name__)


class RedisClient:
    """
    Redis client for chat application.
    
    Handles:
    - Message caching (recent messages)
    - Online presence
    - Typing indicators
    - Unread counts
    """
    
    _instance: Optional['RedisClient'] = None
    _redis: Optional[redis.Redis] = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Initialize Redis connection."""
        if self._redis is not None:
            return
        
        if not settings.REDIS_ENABLE:
            logger.info("Redis is disabled")
            return
        
        try:
            self._redis = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self._redis.ping()
            logger.info(f"✅ Redis connected: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self._redis = None
    
    async def disconnect(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            logger.info("Redis disconnected")
            self._redis = None
    
    # ============ Message Caching ============
    
    async def cache_message(self, room_id: int, message: Dict[str, Any]):
        """
        Cache message in Redis for fast retrieval.
        Uses sorted set with timestamp as score.
        """
        if not self._redis:
            return
        
        try:
            key = f"room:{room_id}:messages"
            message_json = json.dumps(message)
            score = datetime.fromisoformat(message['created_at']).timestamp()
            
            # Add to sorted set
            await self._redis.zadd(key, {message_json: score})
            
            # Keep only recent N messages
            await self._redis.zremrangebyrank(
                key,
                0,
                -(settings.REDIS_MAX_MESSAGES_PER_ROOM + 1)
            )
            
            # Set TTL
            await self._redis.expire(key, settings.REDIS_CHAT_MESSAGE_TTL)
        except Exception as e:
            logger.error(f"Failed to cache message for room {room_id}: {e}")
            # Don't re-raise - caching failure shouldn't break message sending
    
    async def get_cached_messages(
        self,
        room_id: int,
        limit: int = 50,
        before_timestamp: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Get recent messages from Redis cache."""
        if not self._redis:
            return []
        
        try:
            key = f"room:{room_id}:messages"
            
            # Get messages before timestamp (or latest)
            if before_timestamp:
                messages = await self._redis.zrevrangebyscore(
                    key,
                    max=before_timestamp,
                    min='-inf',
                    start=0,
                    num=limit
                )
            else:
                messages = await self._redis.zrevrange(key, 0, limit - 1)
            
            return [json.loads(m) for m in messages]
        except Exception as e:
            logger.error(f"Failed to get cached messages for room {room_id}: {e}")
            return []  # Return empty list on cache failure
    
    # ============ Online Presence ============
    
    async def set_user_online(self, user_id: int):
        """Mark user as online."""
        if not self._redis:
            return
        
        await self._redis.sadd("online_users", str(user_id))
        await self._redis.setex(
            f"user:{user_id}:presence",
            settings.REDIS_PRESENCE_TTL,
            "online"
        )
    
    async def set_user_offline(self, user_id: int):
        """Mark user as offline."""
        if not self._redis:
            return
        
        await self._redis.srem("online_users", str(user_id))
        await self._redis.delete(f"user:{user_id}:presence")
    
    async def is_user_online(self, user_id: int) -> bool:
        """Check if user is online."""
        if not self._redis:
            return False
        
        return await self._redis.sismember("online_users", str(user_id))
    
    async def get_online_users(self) -> List[int]:
        """Get all online user IDs."""
        if not self._redis:
            return []
        
        user_ids = await self._redis.smembers("online_users")
        return [int(uid) for uid in user_ids]
    
    # ============ Typing Indicators ============
    
    async def set_typing(self, room_id: int, user_id: int, is_typing: bool = True):
        """Set typing indicator for user in room."""
        if not self._redis:
            return
        
        key = f"typing:room:{room_id}:user:{user_id}"
        
        if is_typing:
            await self._redis.setex(key, settings.REDIS_TYPING_INDICATOR_TTL, "1")
        else:
            await self._redis.delete(key)
    
    async def get_typing_users(self, room_id: int) -> List[int]:
        """Get users currently typing in room."""
        if not self._redis:
            return []
        
        pattern = f"typing:room:{room_id}:user:*"
        keys = await self._redis.keys(pattern)
        
        # Extract user IDs from keys
        user_ids = []
        for key in keys:
            parts = key.split(":")
            if len(parts) == 5:  # typing:room:123:user:456
                user_ids.append(int(parts[4]))
        
        return user_ids
    
    # ============ Unread Counts ============
    
    async def increment_unread(self, user_id: int, room_id: int, count: int = 1):
        """Increment unread message count for user in room."""
        if not self._redis:
            return
        
        await self._redis.hincrby(f"unread:{user_id}", str(room_id), count)
    
    async def get_unread_count(self, user_id: int, room_id: int) -> int:
        """Get unread count for user in room."""
        if not self._redis:
            return 0
        
        count = await self._redis.hget(f"unread:{user_id}", str(room_id))
        return int(count) if count else 0
    
    async def reset_unread(self, user_id: int, room_id: int):
        """Reset unread count for user in room."""
        if not self._redis:
            return
        
        await self._redis.hdel(f"unread:{user_id}", str(room_id))
    
    async def get_all_unread_counts(self, user_id: int) -> Dict[int, int]:
        """Get all unread counts for user."""
        if not self._redis:
            return {}
        
        counts = await self._redis.hgetall(f"unread:{user_id}")
        return {int(room_id): int(count) for room_id, count in counts.items()}


# Global Redis client instance
redis_client = RedisClient()
