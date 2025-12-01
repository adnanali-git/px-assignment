from fastapi import FastAPI, Path
from typing import Annotated
from httpx import AsyncClient
from asyncio import gather

from models import Response_Status, VendorA_Wrapped_Response, VendorB_Wrapped_Response
from constants import Constants
from service import GetBestVendor

app = FastAPI()

# async call to vendorA
async def call_VendorA() -> VendorA_Wrapped_Response:
    try:
        async with AsyncClient() as clientA:
            respA = await clientA.get(Constants.VENDORA_ENDPOINT)
            respA.raise_for_status() # gets caught in the next block if HTTP Error

            # success
            return VendorA_Wrapped_Response(
                vendor_name=Constants.VENDORA_NAME, 
                response_status=Response_Status.success,
                response_body=respA.json()
            )
    except BaseException as errA:
        return VendorA_Wrapped_Response(
                vendor_name=Constants.VENDORA_NAME, 
                response_status=Response_Status.error, # error
                response_body=errA # for further processing if needed
            )

# async call to vendorB
async def call_VendorB() -> VendorB_Wrapped_Response:
    try:
        async with AsyncClient() as clientB:
            respB = await clientB.get(Constants.VENDORB_ENDPOINT)
            respB.raise_for_status() # gets caught in the next block if HTTP Error

            # success
            return VendorB_Wrapped_Response(
                vendor_name=Constants.VENDORB_NAME, 
                response_status=Response_Status.success,
                response_body=respB.json()
            )
    except BaseException as errB: 
        return VendorB_Wrapped_Response(
                vendor_name=Constants.VENDORB_NAME, 
                response_status=Response_Status.error, # error
                response_body=errB # for further processing if needed
            )

'''
Even though currently the logic for both the above functions is similar,
separating them into two different funcs serves well for future usecases 
which might require extra logic unique to each vendor (separation of concerns)
'''

@app.get("/products/{sku}")
async def get_sku(sku: Annotated[str, Path(min_length=3, max_length=20, pattern="^[a-zA-Z0-9]+$")]) -> str: # return type can be made into an Enum also if the vendors don't change frequently
    # catch: if the order of vendors is changed or new vendors added, the type needs to be changed in all
    # the service functions which utilise it, afaik it cannot be generalised beyond this due to the varying
    # response structures of the vendors (unless we use "Any" type for the "response_body" field)
    results = await gather(
        call_VendorA(), 
        call_VendorB(),
        # return_exceptions=True, # to run all tasks to completion, even if some raise exceptions 
    )

    # the business logic to apply over the results[] tuple
    return GetBestVendor.get_best_vendor(results)