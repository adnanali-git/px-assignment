
from httpx import Response
from pydantic import ValidationError

from app.schemas.vendor import vendorA

def validate_http_response(resp: Response) -> bool:
    try:
        vendorA.VendorAResponse.model_validate(resp)
        return True
    except ValidationError: # [TODO] log the error message 
        raise
