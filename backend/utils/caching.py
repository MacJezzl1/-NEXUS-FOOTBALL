"""
⚽ NEXUS FOOTBALL — Caching & Rate Limiting System
Redis-based caching with smart invalidation and rate limiting
"""

from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
import redis
import json
import logging
from typing import Optional, Callable, Any
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)

# ━━━━━ REDIS CONNECTION ━━━━━

class CacheManager:
    """Manage caching with Redis"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("✅ Redis cache connected")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {str(e)}")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
        
        return None
    
    def set(self, key: str, value: Any, ttl_minutes: int = 60):
        """Set value in cache with TTL"""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.setex(
                key,
                timedelta(minutes=ttl_minutes),
                json.dumps(value, default=str)
            )
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
    
    def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        if not self.redis_client:
            return
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Cache pattern delete error: {str(e)}")
    
    def clear(self):
        """Clear all cache"""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.flushdb()
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")

# ━━━━━ RATE LIMITING ━━━━━

class RateLimiter:
    """Rate limiting with Redis"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
    
    def is_rate_limited(
        self,
        identifier: str,
        limit: int = 100,
        window_minutes: int = 1
    ) -> bool:
        """Check if request is rate limited"""
        key = f"rate_limit:{identifier}"
        
        count = self.cache.get(key) or 0
        
        if count >= limit:
            return True
        
        self.cache.set(key, count + 1, ttl_minutes=window_minutes)
        return False
    
    def get_remaining(self, identifier: str, limit: int = 100) -> int:
        """Get remaining requests"""
        key = f"rate_limit:{identifier}"
        count = self.cache.get(key) or 0
        return max(0, limit - count)

# ━━━━━ CACHE DECORATOR ━━━━━

def cached(ttl_minutes: int = 60, key_prefix: str = "cache"):
    """Decorator for caching function results"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_manager = CacheManager()
            
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}"
            
            if kwargs:
                cache_key += ":" + hashlib.md5(
                    json.dumps(kwargs, sort_keys=True, default=str).encode()
                ).hexdigest()
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_key, result, ttl_minutes=ttl_minutes)
            logger.debug(f"Cache miss: {cache_key}")
            
            return result
        
        return async_wrapper
    
    return decorator

# ━━━━━ RATE LIMIT MIDDLEWARE ━━━━━

async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to requests"""
    
    # Get client identifier (IP or user_id)
    client_ip = request.client.host if request.client else "unknown"
    
    # Check authorization header for user_id
    auth_header = request.headers.get("authorization", "")
    identifier = auth_header.replace("Bearer ", "") or client_ip
    
    # Rate limits per endpoint
    rate_limits = {
        "/api/v1/pitchoracle/predict": {"limit": 100, "window": 1},
        "/api/v1/statpulse/leaderboard": {"limit": 50, "window": 1},
        "/api/v1/matchmind/generate-report": {"limit": 10, "window": 1},
    }
    
    # Get rate limit for this endpoint
    limit_config = rate_limits.get(request.url.path, {"limit": 1000, "window": 1})
    
    rate_limiter = RateLimiter(CacheManager())
    
    # Check rate limit
    if rate_limiter.is_rate_limited(
        identifier,
        limit=limit_config["limit"],
        window_minutes=limit_config["window"]
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    # Add remaining to response headers
    remaining = rate_limiter.get_remaining(identifier, limit=limit_config["limit"])
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response

# ━━━━━ CACHE INVALIDATION ━━━━━

class CacheInvalidator:
    """Smart cache invalidation"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
    
    def invalidate_predictions(self):
        """Invalidate all prediction caches"""
        self.cache.delete_pattern("cache:predict*")
    
    def invalidate_player_ratings(self):
        """Invalidate all player rating caches"""
        self.cache.delete_pattern("cache:rate*")
    
    def invalidate_leaderboards(self):
        """Invalidate leaderboard caches"""
        self.cache.delete_pattern("cache:leaderboard*")
    
    def invalidate_match(self, match_id: str):
        """Invalidate caches for specific match"""
        self.cache.delete_pattern(f"cache:*{match_id}*")
    
    def invalidate_user(self, user_id: str):
        """Invalidate caches for specific user"""
        self.cache.delete_pattern(f"cache:*{user_id}*")
    
    def invalidate_all(self):
        """Invalidate all caches"""
        self.cache.clear()

# ━━━━━ CACHE STATISTICS ━━━━━

class CacheStats:
    """Track cache performance"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.hits = 0
        self.misses = 0
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate percentage"""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_percentage": self.get_hit_rate(),
            "total_requests": self.hits + self.misses
        }

# ━━━━━ GLOBAL INSTANCES ━━━━━

cache_manager = CacheManager()
rate_limiter = RateLimiter(cache_manager)
cache_invalidator = CacheInvalidator(cache_manager)
cache_stats = CacheStats(cache_manager)

# ━━━━━ EXAMPLE USAGE ━━━━━

# In your API endpoints:
#
# @router.get("/predictions/cached")
# @cached(ttl_minutes=60, key_prefix="predictions")
# async def get_cached_predictions():
#     # This result will be cached for 60 minutes
#     return {"predictions": [...]}
#
# When data changes, invalidate cache:
# cache_invalidator.invalidate_predictions()
