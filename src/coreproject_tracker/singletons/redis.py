from typing import Optional

from redis import Redis


class RedisConnectionManager:
    _instance: Optional["RedisConnectionManager"] = None
    _redis_client: Optional[Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisConnectionManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls):
        """Initialize the Redis connection if it doesn't exist"""
        if cls._redis_client is None:
            cls._redis_client = Redis(
                host="localhost", port=6379, decode_responses=True
            )

    @classmethod
    def get_client(cls) -> Redis:
        """Get the Redis client instance"""

        if cls._redis_client is None:
            raise RuntimeError("Redis client not initialized. Call initialize() first")
        return cls._redis_client

    @classmethod
    async def cleanup(cls):
        """Cleanup the Redis connection"""
        if cls._redis_client is not None:
            await cls._redis_client.close()
            cls._redis_client = None
