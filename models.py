from pydantic import BaseModel
from enum import Enum

# VendorA response structure
class VendorA_Response(BaseModel):
    product_id: int
    product_name: str
    product_description: str | None = None
    price: float
    inventory: int | None 
    product_in_stock: bool

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