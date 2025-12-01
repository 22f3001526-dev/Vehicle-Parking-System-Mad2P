"""
Redis Cache Utilities
Makes the app faster by storing frequently-accessed data in memory

Student Project - Performance Optimization
Note: App works fine even if Redis is not running (graceful fallback)
"""

import redis
import json
import functools
from flask import request
from config import Config

# Try to connect to Redis
# If Redis is not running, we'll just skip caching
try:
    redis_client = redis.Redis.from_url(Config.REDIS_URL, decode_responses=True)
    redis_client.ping()  # Test connection
    print("✓ Redis cache connected successfully!")
except redis.ConnectionError:
    print("⚠ Warning: Redis not available - caching disabled")
    redis_client = None

def is_redis_available():
    """
    Check if Redis server is running
    
    Returns:
        True if Redis is available, False otherwise
    """
    return redis_client is not None

def create_cache_key(*args, **kwargs):
    """
    Creates a unique cache key from function arguments
    This helps us store and retrieve the right cached data
    
    Returns:
        String key for Redis
    """
    # Combine all arguments into a single key
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
    return ":".join(key_parts)

def invalidate_cache(pattern):
    """
    Clears cached data matching a pattern
    Call this when data changes to keep cache fresh
    
    Args:
        pattern: Redis key pattern like "lots:*" or "spots:*"
    
    Example:
        invalidate_cache('user:lots:available:*')  # Clear all cached lot data
    """
    if not is_redis_available():
        return  # Can't invalidate if Redis isn't running
    
    try:
        # Find all keys matching the pattern
        keys = redis_client.keys(pattern)
        if keys:
            # Delete all matching keys
            redis_client.delete(*keys)
            print(f"✓ Cleared {len(keys)} cached items matching '{pattern}'")
    except Exception as e:
        print(f"⚠ Cache clear error: {e}")

def clear_all_cache():
    """
    Clears the entire cache
    Use this carefully - only for maintenance/debugging
    """
    if not is_redis_available():
        return
    
    try:
        redis_client.flushdb()
        print("✓ All cache cleared")
    except Exception as e:
        print(f"⚠ Cache clear error: {e}")

def get_cache_stats():
    """
    Gets statistics about cache usage
    Useful for monitoring performance
    
    Returns:
        Dictionary with cache statistics
    """
    if not is_redis_available():
        return {
            'status': 'unavailable',
            'message': 'Redis server not connected'
        }
    
    try:
        info = redis_client.info()
        return {
            'status': 'connected',
            'memory_used': info.get('used_memory_human', 'N/A'),
            'total_keys': redis_client.dbsize(),
            'cache_hits': info.get('keyspace_hits', 0),
            'cache_misses': info.get('keyspace_misses', 0)
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
