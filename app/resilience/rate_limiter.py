
from time import time
from redis.asyncio import Redis

from app.switch import switch

'''
Q. Where does the request argument come from in FastAPI?
- FastAPI automatically injects the Request object when you include it as a parameter in a route function or a dependency.
- You do not create it manually. FastAPI gives you the object for the current HTTP request.
'''

async def exceeds_rate_limit(vendor_name: str, redis_client: Redis) -> bool:
    # local variables to avoid long names to make code more readable
    WINDOW = switch.RateLimitParams.GLOBAL_WINDOW_IN_MILLIS
    REQUEST_LIMIT = switch.RateLimitParams.GLOBAL_REQUEST_LIMIT

    now = time() # current timestamp in millis
    window_start = now - WINDOW # requests older than window_start i.e. less than it need to be removed
    redis_key = f"rate_limit_store:{vendor_name}" # the redis_key [TODO] make "rate_limit_store:" a value picked from .env file or Constants

    # step 1: Count active elements
    count = await redis_client.zcount(redis_key, window_start, now)

    # step 2: check rate-limit
    if count >= REQUEST_LIMIT: # ideally == should suffice
        return True
    else: # step 3: Add current timestamp
        await redis_client.zadd(redis_key, {str(now): now})

    # step 4: Remove timestamps outside sliding window
    await redis_client.zremrangebyscore(redis_key, 0, window_start)

    return False
