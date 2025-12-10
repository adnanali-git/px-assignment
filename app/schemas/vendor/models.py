
from enum import Enum
from typing import NamedTuple, Any

# whether the api response was success or error
class ResponseStatus(str, Enum):
    success = "SUCCESS"
    error = "ERROR"

# tuple from vendor-response for further processing
class GenericVendorResponse(NamedTuple):
    vendor_name: str
    response_status: ResponseStatus
    response_body: Any # refer to main branch for further discussion, this is for cleaner, more practical and readable code

class NormalizedVendorResponse:
    vendor_name: str = ""
    product_id: str = ""
    price: float = -1.0
    inventory: int = 0
    stock_status: bool = False
    last_updated: int = 0 # freshness timestamp in milliseconds
