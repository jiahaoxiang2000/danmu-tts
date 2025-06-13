"""Cache manager for TTS audio caching"""

import asyncio
import logging
import time
import pickle
from typing import Optional, Dict, Any
from pathlib import Path
from .config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching of TTS audio data"""

    def __init__(self):
        self.cache_type = settings.performance.cache.type
        self.max_size_mb = settings.performance.cache.max_size_mb
        self.ttl_seconds = settings.performance.cache.ttl_seconds

        # Memory cache
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_stats = {"hits": 0, "misses": 0, "size_mb": 0}

        # File cache directory
        self.cache_dir = Path("cache")

    async def initialize(self):
        """Initialize cache manager"""
        logger.info(f"Initializing cache manager (type: {self.cache_type})")

        if self.cache_type == "file":
            self.cache_dir.mkdir(exist_ok=True)

        elif self.cache_type == "redis":
            try:
                import redis.asyncio as redis

                self.redis = redis.Redis(host="localhost", port=6379, db=0)
                await self.redis.ping()
                logger.info("Redis cache connected")
            except ImportError:
                logger.warning("Redis not installed, falling back to memory cache")
                self.cache_type = "memory"
            except Exception as e:
                logger.warning(
                    f"Redis connection failed: {e}, falling back to memory cache"
                )
                self.cache_type = "memory"

        # Start cleanup task for memory cache
        if self.cache_type == "memory":
            asyncio.create_task(self._cleanup_task())

        logger.info("Cache manager initialized")

    async def get(self, key: str) -> Optional[str]:
        """Get cached audio data"""
        if not settings.performance.cache.enabled:
            return None

        try:
            if self.cache_type == "memory":
                return await self._get_memory(key)
            elif self.cache_type == "file":
                return await self._get_file(key)
            elif self.cache_type == "redis":
                return await self._get_redis(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")

        self.cache_stats["misses"] += 1
        return None

    async def set(self, key: str, data: str) -> bool:
        """Set cached audio data"""
        if not settings.performance.cache.enabled:
            return False

        try:
            if self.cache_type == "memory":
                return await self._set_memory(key, data)
            elif self.cache_type == "file":
                return await self._set_file(key, data)
            elif self.cache_type == "redis":
                return await self._set_redis(key, data)
        except Exception as e:
            logger.error(f"Cache set error: {e}")

        return False

    async def _get_memory(self, key: str) -> Optional[str]:
        """Get from memory cache"""
        if key in self.memory_cache:
            entry = self.memory_cache[key]

            # Check TTL
            if time.time() - entry["timestamp"] < self.ttl_seconds:
                self.cache_stats["hits"] += 1
                return entry["data"]
            else:
                # Expired
                del self.memory_cache[key]

        return None

    async def _set_memory(self, key: str, data: str) -> bool:
        """Set in memory cache"""
        # Estimate size (rough approximation)
        data_size_mb = len(data.encode()) / (1024 * 1024)

        # Check if adding this would exceed cache size
        if self.cache_stats["size_mb"] + data_size_mb > self.max_size_mb:
            await self._evict_memory()

        self.memory_cache[key] = {
            "data": data,
            "timestamp": time.time(),
            "size_mb": data_size_mb,
        }

        self.cache_stats["size_mb"] += data_size_mb
        return True

    async def _get_file(self, key: str) -> Optional[str]:
        """Get from file cache"""
        cache_file = self.cache_dir / f"{key}.cache"

        if cache_file.exists():
            # Check file age
            file_age = time.time() - cache_file.stat().st_mtime
            if file_age < self.ttl_seconds:
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        self.cache_stats["hits"] += 1
                        return f.read()
                except Exception as e:
                    logger.error(f"Failed to read cache file {cache_file}: {e}")
            else:
                # Expired, remove file
                cache_file.unlink(missing_ok=True)

        return None

    async def _set_file(self, key: str, data: str) -> bool:
        """Set in file cache"""
        cache_file = self.cache_dir / f"{key}.cache"

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(data)
            return True
        except Exception as e:
            logger.error(f"Failed to write cache file {cache_file}: {e}")
            return False

    async def _get_redis(self, key: str) -> Optional[str]:
        """Get from Redis cache"""
        try:
            data = await self.redis.get(f"tts:{key}")
            if data:
                self.cache_stats["hits"] += 1
                return data.decode("utf-8")
        except Exception as e:
            logger.error(f"Redis get error: {e}")

        return None

    async def _set_redis(self, key: str, data: str) -> bool:
        """Set in Redis cache"""
        try:
            await self.redis.setex(f"tts:{key}", self.ttl_seconds, data)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    async def _evict_memory(self):
        """Evict old entries from memory cache"""
        if not self.memory_cache:
            return

        # Sort by timestamp (oldest first)
        sorted_keys = sorted(
            self.memory_cache.keys(), key=lambda k: self.memory_cache[k]["timestamp"]
        )

        # Remove oldest entries until under size limit
        target_size = self.max_size_mb * 0.8  # Keep 20% buffer

        for key in sorted_keys:
            if self.cache_stats["size_mb"] <= target_size:
                break

            entry = self.memory_cache.pop(key)
            self.cache_stats["size_mb"] -= entry["size_mb"]

        logger.info(f"Cache evicted, current size: {self.cache_stats['size_mb']:.2f}MB")

    async def _cleanup_task(self):
        """Background task to clean up expired entries"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes

                current_time = time.time()
                expired_keys = [
                    key
                    for key, entry in self.memory_cache.items()
                    if current_time - entry["timestamp"] > self.ttl_seconds
                ]

                for key in expired_keys:
                    entry = self.memory_cache.pop(key)
                    self.cache_stats["size_mb"] -= entry["size_mb"]

                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / max(total_requests, 1)) * 100

        return {
            "type": self.cache_type,
            "hit_rate": hit_rate,
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "size_mb": self.cache_stats["size_mb"],
            "max_size_mb": self.max_size_mb,
            "entries": (
                len(self.memory_cache) if self.cache_type == "memory" else "unknown"
            ),
        }

    async def clear(self):
        """Clear all cache"""
        if self.cache_type == "memory":
            self.memory_cache.clear()
            self.cache_stats["size_mb"] = 0
        elif self.cache_type == "file":
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink(missing_ok=True)
        elif self.cache_type == "redis":
            try:
                await self.redis.flushdb()
            except Exception as e:
                logger.error(f"Failed to clear Redis cache: {e}")

        self.cache_stats["hits"] = 0
        self.cache_stats["misses"] = 0
        logger.info("Cache cleared")

    async def cleanup(self):
        """Cleanup cache manager"""
        if hasattr(self, "redis"):
            await self.redis.close()
        logger.info("Cache manager cleaned up")
