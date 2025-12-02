from fastapi import FastAPI, Path
from typing import Annotated
from httpx import AsyncClient
from asyncio import gather, sleep
from jsonpickle import decode
from random import uniform
from tenacity import retry, stop_after_attempt, wait_fixed

from models import ResponseStatus, GenericVendorResponse, CaseForVendorC
from constants import Constants
from service import GetBestVendor
from cache import RedisCache
from simulators import SimulatorA, SimulatorB, SimulatorC
from switch import SwitchValues

app = FastAPI()

# retry logic
retry_policy = retry(
    stop=stop_after_attempt(1 + Constants.VENDOR_API_RETRIES),
    wait=wait_fixed(Constants.DELAY_BETWEEN_RETRIES)
)

# async call to vendorA
@retry_policy
async def call_vendorA(sku: str) -> GenericVendorResponse:
    # mock via json-files
    if SwitchValues.IS_MOCKING_VIA_FILE:
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
        try:
            async with AsyncClient(timeout=Constants.VENDOR_API_TIMEOUT) as clientA:
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
    if SwitchValues.IS_MOCKING_VIA_FILE:
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
        try:
            async with AsyncClient(timeout=Constants.VENDOR_API_TIMEOUT) as clientB:
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

# async call to vendorC
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
        try:
            async with AsyncClient(timeout=Constants.VENDOR_API_TIMEOUT) as clientC:
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
    redis_client = RedisCache()
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