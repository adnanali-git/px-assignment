from redis.asyncio import Redis
from app.config.config import settings

def fetch_key_for_best_vendor_namespace() -> str:
    return "sku:"

async def get_best_vendor_for_sku_from_redis(redis: Redis, sku: str) -> str | None:
    key_namespace = fetch_key_for_best_vendor_namespace()
    cache_key = f"{key_namespace}{sku}"
    value = await redis.get(cache_key)
    if value: # is found
        return value # return it
    return None # else return None

async def set_best_vendor_for_sku_in_redis(redis: Redis, sku: str, vendor_name: str, ttl: int = settings.cache_ttl):
    key_namespace = fetch_key_for_best_vendor_namespace()
    cache_key = f"{key_namespace}{sku}"
    await redis.set(cache_key, vendor_name, ex=ttl)