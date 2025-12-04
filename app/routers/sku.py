
from fastapi import APIRouter, Depends, Path
from redis.asyncio import Redis

from app.services.sku_service import SKUService
from app.core.dependencies import get_redis

router = APIRouter()
sku_service = SKUService()

async def validate_sku(
    sku: str = Path(
        ...,                        # <--- tells FastAPI: this is a required func param                
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9]+$"
    )
):
    # Extra business rules if needed
    # if sku.startswith("X"): raise HTTPException(...)
    return sku

# [TODO]: Move validation clutter to a separate function inside this file
# [SOLUTION]: Two: (1) Dependency func OR (2) Type Alias
# Type Alias gives syntactically the cleanest code but cannot accomodate custom business logic
# if required, eg: throw HTTP-4xx if such-and-such condition fails
# if this validation is used by many endpoints in this file, then move it 
# into a dedicated file "validators.py" or smth similar under this directory
@router.get("/products/{sku}")
async def get_sku(sku: str = Depends(validate_sku), redis: Redis = Depends(get_redis)) -> str: # return type can be made into an Enum also if the vendors don't change frequently
    return await sku_service.get_best_vendor_for_sku(sku, redis)
    