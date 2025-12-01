from models import VendorA_Wrapped_Response, VendorB_Wrapped_Response
from constants import Constants

# the business logic resides here
class GetBestVendor:
    @staticmethod
    def match_result_to_func(result: VendorA_Wrapped_Response | VendorB_Wrapped_Response) -> tuple:
        match result.vendor_name:
            case Constants.VENDORA_NAME:
                # process
                # return namedtuple of (stock, price, vendor_name)
            case Constants.VENDORB_NAME:
                # process
                # return namedtuple of (stock, price, vendor_name)

    @staticmethod
    def get_best_vendor(result_tuple: tuple[VendorA_Wrapped_Response, VendorB_Wrapped_Response]) -> str:
        stock_price = [] # list of (stock, price, vendor_name) tuples

        # iterate
        for result in result_tuple:
            stock_price.append(match_result_to_func(result))
        
        # get best vendor from the stock_price list
        # return the vendor name