
from fastapi import Request
from redis.asyncio import Redis

# This function is the only place in the entire app that touches request.app.state.redis
async def get_redis(request: Request) -> Redis:
    return request.app.state.redis

# This ensures:
# - Service layer does not depend on FastAPI (keeps the service layer clean, pure, and testable)
# - The complete Request is not passed around (service functions receive only Redis, not the entire Request structure)
# - Redis is lazily injected
# - Tests can easily inject a mock Redis client
# - Routers control DI, not services (matches ES/Clean Architecture recommended practices)
# - Change only a few lines of code when you want to swap Redis for another provider in the future