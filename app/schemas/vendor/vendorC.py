
from enum import Enum
from pydantic import BaseModel

# VendorC response structure and related substructure definitions
# which case for vendorC
class CaseForVendorC(str, Enum):
    slow = "SLOW"
    fail = "FAIL"
    okay = "SUCCESS"

# stock status
class VendorCStockStatus(str, Enum):
    in_stock = "YES"
    out_of_stock = "OOS"

# other details
class VendorCDetails(BaseModel):
    name: str
    desc: str
    product_price: float
    p_inventory: int
    p_stock: VendorCStockStatus

# main response structure
class VendorCResponse(BaseModel):
    sku_id: str
    details: VendorCDetails
    details_updated_at: int # freshness timestamp in milliseconds
