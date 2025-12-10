
from httpx import Response
from pydantic import ValidationError

from app.schemas.vendor import vendorB

def validate_http_response(resp: Response) -> bool:
    try:
        vendorB.VendorBResponse.model_validate(resp)
        return True
    except ValidationError: # [TODO] log the error message 
        raise
