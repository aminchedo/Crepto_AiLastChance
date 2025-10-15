import json
import logging
from typing import Any, Optional

import redis.asyncio as redis

from config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Redis disconnected")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration."""
        try:
            serialized = json.dumps(value)
            if expire:
                await self.redis.setex(key, expire, serialized)
            else:
                await self.redis.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment value in Redis."""
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis INCREMENT error for key {key}: {e}")
            return 0

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key."""
        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False


# Global Redis client instance
redis_client = RedisClient()
