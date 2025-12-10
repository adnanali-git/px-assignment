
from httpx import AsyncClient
from redis.asyncio import Redis
import app.external_clients.response_validators.vendorB_validator as ResponseValidator
from app.schemas.vendor.models import GenericVendorResponse, ResponseStatus
from app.switch import switch
from app.switch.switch import VendorConstants

def get_vendor_endpoint(name: str) -> str:
    return switch.VendorConstants.VENDOR_ENDPOINTS[name]
    
async def call_vendor(sku: str, redis_client: Redis) -> GenericVendorResponse:
    vendor_name = VendorConstants.VENDORB_NAME
    vendor_endpoint = get_vendor_endpoint(vendor_name)
    try:
        async with AsyncClient() as http_client:
            http_resp = await http_client.get(vendor_endpoint)
            http_resp.raise_for_status() # gets caught in the next block if HTTP Error

            # is the response structure valid? if not, throws ValidationError exception
            # and gets caught in the except block below
            ResponseValidator.validate_http_response(http_resp)

            # success
            return GenericVendorResponse(
                vendor_name=vendor_name, 
                response_status=ResponseStatus.success,
                response_body=http_resp.json()
            )
    except BaseException as err:
        # return response
        """
        what to do in cases of exception is a UI/UX/PM ask
        My assumption: log the error, swallow it and return to calling layer for further handling
        So what to do with errors resides in the service-layer
        """
        return GenericVendorResponse(
            vendor_name=vendor_name, 
            response_status=ResponseStatus.error, # error
            response_body=err # for further processing if needed
        )
