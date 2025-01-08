from typing import Optional

from coreproject_tracker.singletons.redis import RedisConnectionManager


class BaseRedisProtocol:
    """Base mixin for Redis operations"""

    def __init__(self):
        self.redis_client = RedisConnectionManager.get_client()

    async def store_value(
        self, key: str, value: str, ttl: Optional[int] = None
    ) -> bool:
        """
        Store a value in Redis with optional TTL

        Args:
            key: Redis key
            value: Value to store
            ttl: Time to live in seconds (optional)
        """
        if ttl is not None:
            await self.redis_client.setex(key, ttl, value)
        else:
            await self.redis_client.set(key, value)
        return True

    async def get_value(self, key: str) -> str | None:
        """Retrieve a value from Redis"""
        return await self.redis_client.get(key)
