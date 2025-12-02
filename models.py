from pydantic import BaseModel
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

# VendorA response structure
class VendorAResponse(BaseModel):
    product_id: str
    product_name: str
    product_description: str | None = None
    price: float
    inventory: int | None 
    product_in_stock: bool

# VendorB response structure and related substructure definitions
# metadata
class VendorBMetadata(BaseModel):
    title: str
    description: str
    image_details: str

# stock status
class VendorBStockStatus(str, Enum):
    in_stock = "IN_STOCK"
    out_of_stock = "OUT_OF_STOCK"

# inventory and stock details
class VendorBInventory(BaseModel):
    product_inventory: int
    stock_status: VendorBStockStatus

# main response structure
class VendorBResponse(BaseModel):
    id: str
    product_metadata: VendorBMetadata
    cost: float
    inventory: VendorBInventory