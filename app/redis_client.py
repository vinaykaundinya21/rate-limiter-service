import redis
import os
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self._client = None
        self._connect()

    def _connect(self):
        try:
            self._client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=0,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            self._client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Running in fail-open mode.")
            self._client = None

    def is_available(self):
        try:
            if self._client:
                self._client.ping()
                return True
        except Exception:
            self._client = None
        return False

    def get_client(self):
        if not self.is_available():
            self._connect()
        return self._client


redis_instance = RedisClient()

def get_redis():
    return redis_instance.get_client()

def is_redis_available():
    return redis_instance.is_available()