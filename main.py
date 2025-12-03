from fastapi import FastAPI, Path, HTTPException
from typing import Annotated
from httpx import AsyncClient
from asyncio import gather, sleep
from jsonpickle import decode
from random import uniform
from tenacity import retry, stop_after_attempt, wait_fixed
from aiobreaker import CircuitBreaker
from datetime import timedelta
from contextlib import asynccontextmanager
from redis.asyncio import Redis
from time import time

from models import ResponseStatus, GenericVendorResponse, CaseForVendorC
from constants import Constants
from service import GetBestVendor
from cache import RedisCache
from simulators import SimulatorA, SimulatorB, SimulatorC
import switch

# can also use the FastAPI app.state.redis instead of the global var
# but not sure if there are any issues in using that
# global redis_client
redis_client: Redis

# lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # reference to the global variable
    global redis_client

    # setup steps (equivalent to @app.on_startup())
    redis_client = RedisCache().redis
    # client_resp = await redis_client.ping()
    # print(f"Did the client start? {client_resp}")

    try: # the runtime of the app
        yield
    
    finally: # teardown (equivalent to @app.on_shutdown())
        await redis_client.aclose()

app = FastAPI(lifespan=lifespan)

async def exceeds_rate_limit(vendor_name: str) -> bool:
    # local variables to avoid long names to make code more readable
    WINDOW = switch.RateLimitParams.GLOBAL_WINDOW_IN_MILLIS
    REQUEST_LIMIT = switch.RateLimitParams.GLOBAL_REQUEST_LIMIT

    now = time() # current timestamp in millis
    window_start = now - WINDOW # requests older than window_start i.e. less than it need to be removed
    redis_key = f"rate_limit_store:{vendor_name}" # the redis_key [TODO] make "rate_limit_store:" a value picked from .env file or Constants

    global redis_client

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

# retry logic
retry_policy = retry(
    stop=stop_after_attempt(1 + Constants.VENDOR_API_RETRIES),
    wait=wait_fixed(Constants.DELAY_BETWEEN_RETRIES)
)

# async call to vendorA
@retry_policy
async def call_vendorA(sku: str) -> GenericVendorResponse:
    # mock via json-files
    if switch.SwitchValues.IS_MOCKING_VIA_FILE:
        # get mock_file path
        fpath = SimulatorA(sku).mock_file_path
        # read file
        with open(fpath, "r") as mock_file:
            respA = decode(mock_file.read())
        mock_file.close()
        # return response
        return GenericVendorResponse(
                vendor_name=Constants.VENDORA_NAME, 
                response_status=ResponseStatus.success,
                response_body=respA
            )
    else: # mock via actual API calls
        req_headers = None # no request-headers by default
        exceeds_RL = False # doesn't exceed rate limit by default
        if switch.SwitchValues.RATE_LIMIT_FOR_VENDORS_ENABLED:
            req_headers = {"x-api-key": switch.PrivateVault.API_KEY_FOR_VENDORA}
            exceeds_RL = exceeds_rate_limit(Constants.VENDORA_NAME) # test RL for vendor
        try:
            if exceeds_RL: 
                raise HTTPException(
                    429, f"Rate limit exceeded: {switch.RateLimitParams.GLOBAL_REQUEST_LIMIT} requests/min"
                )

            async with AsyncClient(headers=req_headers, timeout=Constants.VENDOR_API_TIMEOUT) as clientA:
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
@retry_policy
async def call_vendorB(sku: str) -> GenericVendorResponse:
    # mock via json-files
    if switch.SwitchValues.IS_MOCKING_VIA_FILE:
        # get mock_file path
        fpath = SimulatorB(sku).mock_file_path
        # read file
        with open(fpath, "r") as mock_file:
            respB = decode(mock_file.read())
        mock_file.close()
        # return response
        return GenericVendorResponse(
                vendor_name=Constants.VENDORB_NAME, 
                response_status=ResponseStatus.success,
                response_body=respB
            )
    else: # mock via actual API calls
        req_headers = None # no request-headers by default
        exceeds_RL = False # doesn't exceed rate limit by default
        if switch.SwitchValues.RATE_LIMIT_FOR_VENDORS_ENABLED:
            req_headers = {"x-api-key": switch.PrivateVault.API_KEY_FOR_VENDORB}
            exceeds_RL = exceeds_rate_limit(Constants.VENDORB_NAME) # test RL for vendor
        try:
            if exceeds_RL: 
                raise HTTPException(
                    429, f"Rate limit exceeded: {switch.RateLimitParams.GLOBAL_REQUEST_LIMIT} requests/min"
                )

            async with AsyncClient(headers=req_headers, timeout=Constants.VENDOR_API_TIMEOUT) as clientB:
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

# circuit breaker for vendorC
vendorC_circuit_breaker = CircuitBreaker(
    fail_max=switch.CircuitBreakerParams.VENDORC_CB_MAX_FAIL, # open after 3 consecutive failures
    timeout_duration=timedelta(
        seconds=switch.CircuitBreakerParams.VENDORC_CB_OPEN_DURATION) # half-open after 30s elapse
)

# async call to vendorC
@vendorC_circuit_breaker
@retry_policy
async def call_vendorC(sku: str) -> GenericVendorResponse:
    # call simulator for vendorC
    sim_vendorC = SimulatorC(sku)

    # mock via json-files
    if sim_vendorC.case_for_vendorC != CaseForVendorC.fail:
        # get mock_file path
        fpath = sim_vendorC.mock_file_path
        # if case = slow, then sleep
        if sim_vendorC.case_for_vendorC == CaseForVendorC.slow:
            await sleep(uniform(0.0, Constants.VENDOR_API_TIMEOUT/2))
            # print("VendorC is slow!")
        # read file
        with open(fpath, "r") as mock_file:
            respC = decode(mock_file.read())
        mock_file.close()
        # return response
        return GenericVendorResponse(
                vendor_name=Constants.VENDORC_NAME, 
                response_status=ResponseStatus.success,
                response_body=respC
            )
    else: # mock via actual API calls
        # print("VendorC must fail!")
        req_headers = None # no request-headers by default
        exceeds_RL = False # doesn't exceed rate limit by default
        if switch.SwitchValues.RATE_LIMIT_FOR_VENDORS_ENABLED:
            req_headers = {"x-api-key": switch.PrivateVault.API_KEY_FOR_VENDORC}
            exceeds_RL = exceeds_rate_limit(Constants.VENDORC_NAME) # test RL for vendor
        try:
            if exceeds_RL: 
                raise HTTPException(
                    429, f"Rate limit exceeded: {switch.RateLimitParams.GLOBAL_REQUEST_LIMIT} requests/min"
                )

            async with AsyncClient(headers=req_headers, timeout=Constants.VENDOR_API_TIMEOUT) as clientC:
                respC = await clientC.get(Constants.VENDORC_ENDPOINT)
                respC.raise_for_status() # gets caught in the next block if HTTP Error

                # success
                return GenericVendorResponse(
                    vendor_name=Constants.VENDORC_NAME, 
                    response_status=ResponseStatus.success,
                    response_body=respC.json()
                )
        except BaseException as errC: 
            return GenericVendorResponse(
                    vendor_name=Constants.VENDORC_NAME, 
                    response_status=ResponseStatus.error, # error
                    response_body=errC # for further processing if needed
                )

@app.get("/products/{sku}")
async def get_sku(sku: Annotated[str, Path(min_length=3, max_length=20, pattern="^[a-zA-Z0-9]+$")]) -> str: # return type can be made into an Enum also if the vendors don't change frequently
    # this block is now more generic after introducing "Any" type for the "response_body" field
    # so no extra code changes required (unlike before) if the order of vendors is altered or new
    # vendors added

    # initialise redis-client
    global redis_client
    cache_key = f"sku:{sku}"

    # Check Redis cache
    best_vendor = await redis_client.get(cache_key)
    if best_vendor:
        # print("Accessed cache")
        return best_vendor

    # Else fetch via API call
    results = await gather(
        call_vendorA(sku), 
        call_vendorB(sku),
        call_vendorC(sku),
        # return_exceptions=True, # to run all tasks to completion, even if some raise exceptions 
    )

    # the business logic to apply over the results[] tuple
    best_vendor = GetBestVendor.get_best_vendor(results)

    # Store in Redis cache with default ttl
    await redis_client.set(cache_key, best_vendor)

    return best_vendor