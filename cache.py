from redis.asyncio import Redis
from config import settings

class RedisCache:
    def __init__(self):
        # initialise the redis-client
        self.redis = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True  # return strings instead of bytes
        )

    async def get(self, key: str) -> str | None:
        value = await self.redis.get(key)
        if value: # is found
            return value # return it
        return None # else return None

    async def set(self, key: str, value: str, ttl: int = settings.cache_ttl):
        await self.redis.set(key, value, ex=ttl)

    # use lifespan event handlers instead
    # didn't use it as I don't yet understand fully how it operates
    async def close(self):
        await self.redis.aclose()