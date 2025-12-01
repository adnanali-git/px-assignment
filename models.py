from pydantic import BaseModel
from enum import Enum
from typing import NamedTuple

# whether the api response was success or error
class Response_Status(str, Enum):
    success = "SUCCESS"
    error = "ERROR"

# VendorA response structure
class VendorA_Response(BaseModel):
    product_id: int
    product_name: str
    product_description: str | None = None
    price: float
    inventory: int | None 
    product_in_stock: bool

# tuple from VendorA response for further processing
class VendorA_Wrapped_Response(NamedTuple):
    vendor_name: str
    response_status: Response_Status
    response_body: VendorA_Response | BaseException

# VendorB response structure and related substructure definitions
# metadata
class VendorB_Metadata(BaseModel):
    title: str
    description: str
    image_details: str

# stock status
class VendorB_Stock_Status(str, Enum):
    in_stock = "IN_STOCK"
    out_of_stock = "OUT_OF_STOCK"

# inventory and stock details
class VendorB_Inventory(BaseModel):
    product_inventory: int
    stock_status: VendorB_Stock_Status

# main response structure
class VendorB_Response(BaseModel):
    id: str
    product_metadata: VendorB_Metadata
    cost: float
    inventory: VendorB_Inventory

# tuple from VendorB response for further processing
class VendorB_Wrapped_Response(NamedTuple):
    vendor_name: str
    response_status: Response_Status
    response_body: VendorB_Response | BaseException