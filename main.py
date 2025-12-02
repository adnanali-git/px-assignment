from fastapi import FastAPI, Path
from typing import Annotated
from httpx import AsyncClient
from asyncio import gather

from models import ResponseStatus, GenericVendorResponse
from constants import Constants
from service import GetBestVendor
from cache import RedisCache

app = FastAPI()

# async call to vendorA
async def call_vendorA() -> GenericVendorResponse:
    try:
        async with AsyncClient() as clientA:
            respA = await clientA.get(Constants.VENDORA_ENDPOINT)
            respA.raise_for_status() # gets caught in the next block if HTTP Error

            # success
            return GenericVendorResponse(
                vendor_name=Constants.VENDORA_NAME, 
                response_status=ResponseStatus.success,
                response_body=respA.json()
            )
    except BaseException as errA:
        return GenericVendorResponse(
                vendor_name=Constants.VENDORA_NAME, 
                response_status=ResponseStatus.error, # error
                response_body=errA # for further processing if needed
            )

# async call to vendorB
async def call_vendorB() -> GenericVendorResponse:
    try:
        async with AsyncClient() as clientB:
            respB = await clientB.get(Constants.VENDORB_ENDPOINT)
            respB.raise_for_status() # gets caught in the next block if HTTP Error

            # success
            return GenericVendorResponse(
                vendor_name=Constants.VENDORB_NAME, 
                response_status=ResponseStatus.success,
                response_body=respB.json()
            )
    except BaseException as errB: 
        return GenericVendorResponse(
                vendor_name=Constants.VENDORB_NAME, 
                response_status=ResponseStatus.error, # error
                response_body=errB # for further processing if needed
            )

'''
Even though currently the logic for both the above functions is similar,
separating them into two different funcs serves well for future usecases 
which might require extra logic unique to each vendor (separation of concerns)
[UPDATE]: The two functions are more easily mergeable now after 
the introduction of Any yet keeping it separate for the same reason mentioned above. 
'''

@app.get("/products/{sku}")
async def get_sku(sku: Annotated[str, Path(min_length=3, max_length=20, pattern="^[a-zA-Z0-9]+$")]) -> str: # return type can be made into an Enum also if the vendors don't change frequently
    # this block is now more generic after introducing "Any" type for the "response_body" field
    # so no extra code changes required (unlike before) if the order of vendors is altered or new
    # vendors added

    # initialise redis-client
    redis_client = RedisCache()
    cache_key = f"sku:{sku}"

    # Check Redis cache
    best_vendor = await redis_client.get(cache_key)
    if best_vendor:
        # print("Accessed cache")
        return best_vendor

    # Else fetch via API call
    results = await gather(
        call_vendorA(), 
        call_vendorB(),
        # return_exceptions=True, # to run all tasks to completion, even if some raise exceptions 
    )

    # the business logic to apply over the results[] tuple
    best_vendor = GetBestVendor.get_best_vendor(results)

    # Store in Redis cache with default ttl
    await redis_client.set(cache_key, best_vendor)

    return best_vendor