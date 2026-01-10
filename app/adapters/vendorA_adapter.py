
from app.schemas.vendor.models import GenericVendorResponse, NormalizedVendorResponse
from app.schemas.vendor.vendorA import VendorAResponse
from app.switch.switch import VendorConstants

class VendorAAdapter:
    def normalize(self, generic_response: GenericVendorResponse) -> NormalizedVendorResponse:
        # cannot be called for a different vendor, else raises error
        assert generic_response.vendor_name == VendorConstants.VENDORA_NAME

        # example structure
        """
        respA: models.VendorAResponse = models.VendorAResponse(
            product_id="",
            product_name="",
            price=0,
            inventory=None,
            product_in_stock=False,
            last_updated=0
        )
        """

        normalized_response = NormalizedVendorResponse()

        # errors handled at the service layer before reaching here
        normalized_response.vendor_name = generic_response.vendor_name

        # validation completed at the API call layer
        respA: VendorAResponse = generic_response.response_body

        # fill all the fields
        normalized_response.product_id = respA.product_id
        normalized_response.price = respA.price
        normalized_response.inventory = 0 if respA.inventory == None else respA.inventory
        normalized_response.stock_status = respA.product_in_stock
        normalized_response.last_updated = respA.last_updated

        # return
        return normalized_response
