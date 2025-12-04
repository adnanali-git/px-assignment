from asyncio import sleep
from random import uniform
from fastapi import HTTPException
from httpx import AsyncClient
from jsonpickle import decode
from tenacity import retry, stop_after_attempt, wait_fixed
from aiobreaker import CircuitBreaker
from datetime import timedelta

from app.core.constants import Constants
from app.core.rate_limiter import exceeds_rate_limit
from app.schemas.vendor.models import CaseForVendorC, GenericVendorResponse, ResponseStatus
from app.switch import switch
from simulation.simulators import SimulatorA, SimulatorB, SimulatorC

# retry logic
retry_policy = retry(
    stop=stop_after_attempt(1 + Constants.VENDOR_API_RETRIES),
    wait=wait_fixed(Constants.DELAY_BETWEEN_RETRIES)
)

# circuit breaker for vendorC
vendorC_circuit_breaker = CircuitBreaker(
    fail_max=switch.CircuitBreakerParams.VENDORC_CB_MAX_FAIL, # open after 3 consecutive failures
    timeout_duration=timedelta(
        seconds=switch.CircuitBreakerParams.VENDORC_CB_OPEN_DURATION) # half-open after 30s elapse
)

class VendorClient:
    # async call to vendorA
    @staticmethod
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
                exceeds_RL = await exceeds_rate_limit(Constants.VENDORA_NAME) # test RL for vendor
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
    @staticmethod
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
                exceeds_RL = await exceeds_rate_limit(Constants.VENDORB_NAME) # test RL for vendor
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

    # async call to vendorC
    @staticmethod
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
                exceeds_RL = await exceeds_rate_limit(Constants.VENDORC_NAME) # test RL for vendor
            try:
                if exceeds_RL: 
                    raise HTTPException(
                        429, f"Rate limit exceeded: {switch.RateLimitParams.GLOBAL_REQUEST_LIMIT} requests/min"
                    )

                async with AsyncClient(headers=req_headers, timeout=Constants.VENDOR_API_TIMEOUT) as clientC:
                    respC = await vendorC_circuit_breaker.call_async(clientC.get, Constants.VENDORC_ENDPOINT)
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
