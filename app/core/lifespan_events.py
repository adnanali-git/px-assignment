
from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis.asyncio import Redis

from app.config.config import settings

redis_client: Redis | None = None

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    global redis_client

    # ---- Startup logic here ----
    redis_client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True
    )

    # Expose redis in app.state (best practice)
    app.state.redis = redis_client

    try: # Yield control to the app
        yield
    
    finally: # ---- Shutdown logic here ----
        if redis_client:
            await redis_client.aclose()
            # print("🔌 Redis connection closed.")
