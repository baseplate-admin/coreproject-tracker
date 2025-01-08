from typing import Optional
import json
from twisted.internet import defer
from coreproject_tracker.singletons.redis import RedisConnectionManager


class BaseRedisProtocol:
    """Base mixin for Redis operations"""

    def __init__(self):
        self.redis_client = RedisConnectionManager.get_client()

    def store_value(
        self, key: str, value: str, ttl: Optional[int] = None
    ) -> defer.Deferred:
        """
        Store a value in Redis with optional TTL.

        Args:
            key: Redis key
            value: Value to store
            ttl: Time to live in seconds (optional)
        """
        if isinstance(value, dict):
            value = json.dumps(value)

        # This function returns a Deferred because Redis operations are asynchronous
        def _store_value():
            if ttl is not None:
                return self.redis_client.setex(key, ttl, value)
            else:
                return self.redis_client.set(key, value)

        # Use defer.succeed() to return a Deferred
        return defer.ensureDeferred(_store_value())

    def get_value(self, key: str) -> defer.Deferred:
        """Retrieve a value from Redis"""

        def _get_value():
            return self.redis_client.get(key)

        return defer.ensureDeferred(_get_value())
