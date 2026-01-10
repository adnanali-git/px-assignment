
from typing import Protocol
from app.schemas.vendor.models import GenericVendorResponse, NormalizedVendorResponse

class BaseAdapter(Protocol):
    """
    Adapter interface to normalize GenericVendorResponse to NormalizedVendorResponse
    """
    def normalize(self, generic_response: GenericVendorResponse) -> NormalizedVendorResponse:
        ...
