
from enum import Enum
from pydantic import BaseModel

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
    last_refresh_time: int # freshness timestamp in milliseconds
