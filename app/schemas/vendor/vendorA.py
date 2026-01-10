# VendorA response structure
from pydantic import BaseModel

class VendorAResponse(BaseModel):
    product_id: str
    product_name: str
    product_description: str | None = None
    price: float
    inventory: int | None 
    product_in_stock: bool
    last_updated: int # freshness timestamp in milliseconds