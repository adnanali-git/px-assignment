
from app.schemas.vendor.models import GenericVendorResponse, NormalizedVendorResponse
from app.schemas.vendor.vendorB import VendorBResponse, VendorBStockStatus
from app.switch.switch import VendorConstants

class VendorBAdapter:
    def normalize(self, generic_response: GenericVendorResponse) -> NormalizedVendorResponse:
        # cannot be called for a different vendor, else raises error
        assert generic_response.vendor_name == VendorConstants.VENDORB_NAME

        # example structure
        """
        respB: models.VendorBResponse = models.VendorBResponse(
            id="",
            product_metadata=models.VendorBMetadata(
                title="",
                description="",
                image_details=""
            ),
            cost=0,
            inventory=models.VendorBInventory(
                product_inventory=0,
                stock_status=models.VendorBStockStatus.out_of_stock
            ),
            last_refresh_time=0
        )
        """

        normalized_response = NormalizedVendorResponse()

        # errors handled at the service layer before reaching here
        normalized_response.vendor_name = generic_response.vendor_name

        # validation completed at the API call layer
        respB: VendorBResponse = generic_response.response_body

        # fill all the fields
        normalized_response.product_id = respB.id
        normalized_response.price = respB.cost
        normalized_response.inventory = respB.inventory.product_inventory
        normalized_response.stock_status = False if respB.inventory.stock_status == VendorBStockStatus.out_of_stock else True
        normalized_response.last_updated = respB.last_refresh_time

        # return
        return normalized_response
