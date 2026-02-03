"""Redis cache implementation for EdiLink FastAPI application.

This module provides Redis-based caching functionality using fastapi-cache2.
"""

import os
from typing import Any, cast

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis, from_url

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


async def init_cache() -> None:
    """Initialize the FastAPI cache with Redis backend.

    Should be called during application startup event.
    Skip initialization in test environment (CI).
    """
    if os.getenv("CI") == "true":
        return
    redis_client: Redis = from_url(REDIS_URL, decode_responses=True)
    FastAPICache.init(RedisBackend(redis_client), prefix="edinet")


async def get_cache_client() -> Redis:
    """Get the Redis client instance for manual cache operations.

    Returns:
        Redis: Async Redis client instance.
    """
    return cast(Redis, from_url(REDIS_URL, decode_responses=True))


async def clear_cache(pattern: str | None = None) -> None:
    """Clear cache entries from Redis.

    Args:
        pattern: Optional pattern to match keys for deletion.
                If None, clears all cache entries with 'edinet*' prefix.
    """
    redis_client = await get_cache_client()

    search_pattern = pattern if pattern else "edinet*"

    cursor = 0
    keys_to_delete = []

    while True:
        cursor, keys = await redis_client.scan(cursor, match=search_pattern, count=100)
        keys_to_delete.extend(keys)

        if cursor == 0:
            break

    if keys_to_delete:
        await redis_client.delete(*keys_to_delete)

    await redis_client.close()


async def cache_get(key: str) -> Any | None:
    """Get a value from cache by key.

    Args:
        key: The cache key to retrieve.

    Returns:
        The cached value or None if not found.
    """
    redis_client = await get_cache_client()
    value = await redis_client.get(key)
    await redis_client.close()
    return value


async def cache_set(key: str, value: str, expire: int | None = None) -> bool:
    """Set a value in cache.

    Args:
        key: The cache key.
        value: The value to store.
        expire: Optional expiration time in seconds.

    Returns:
        True if successful, False otherwise.
    """
    redis_client = await get_cache_client()
    result = await redis_client.set(key, value, ex=expire)
    await redis_client.close()
    return result is not None


async def cache_delete(key: str) -> int:
    """Delete a specific key from cache.

    Args:
        key: The cache key to delete.

    Returns:
        Number of keys deleted (0 or 1).
    """
    redis_client = await get_cache_client()
    result = await redis_client.delete(key)
    await redis_client.close()
    return cast(int, result)
