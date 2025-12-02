import models
from constants import Constants
from typing import NamedTuple
from time import time_ns

class InvalidResponseStructure(Exception):
    pass

class InvalidVendorException(Exception):
    pass

class NormalizedParams(NamedTuple):
    stock: int
    price: float
    vendor_name: str

# the business logic resides here
class GetBestVendor:
    @staticmethod
    def is_timestamp_fresh(timestamp: int) -> bool:
        if (time_ns() - timestamp * 1_000_000) > Constants.FRESHNESS_LIMIT * 1_000_000_000:
            return False
        return True
    
    @staticmethod
    def get_best_vendor_from_normalized_tuple_list(normalized_tuple_list: list[NormalizedParams]) -> str:
        # drop all tuples with stock = 0
        iter1 = [tup for tup in normalized_tuple_list if tup.stock > 0]

        # check if the list is empty, then return OOS message
        if not iter1: return Constants.BEST_VENDOR_SELECTION_OOS_MESSAGE

        # else proceed to further filtering
        # sort asc by price, if tie then sort desc by stock hence minus sign
        best_vendor = sorted(iter1, key=lambda tup: (tup.price, -tup.stock))[0].vendor_name
        return best_vendor

    @staticmethod
    def validate_price(price: float) -> bool:
        try:
            float(price)
            return (price > 0)
        except ValueError:
            return False

    @staticmethod
    def normalize_response_for_vendorA(resp: models.GenericVendorResponse) -> NormalizedParams:
        vname = Constants.VENDORA_NAME # vendor_name, declared as variable for easier reuse

        assert(resp.vendor_name == vname) # this will break if someone updates the code erroneously

        # default values
        stockA: int = 0
        priceA: float = 0

        # no retries implemented yet so stock treated as 0
        if resp.response_status == models.ResponseStatus.error: 
            return NormalizedParams(stock=stockA, price=priceA, vendor_name=vname)
        
        # logic specific to the response structure of vendorA
        # validate the response structure
        try:
            respA = models.VendorAResponse.model_validate(resp.response_body)
        except Exception as e:
            raise InvalidResponseStructure("Error validating the response body for vendorA: {}".format(e))

        # timestamp validation comes first to avoid any further delays
        if not GetBestVendor.is_timestamp_fresh(respA.last_updated): # stale date => discard
            return NormalizedParams(stock=0, price=priceA, vendor_name=vname)
        
        # stock normalisation
        if (respA.inventory == 0 and respA.product_in_stock): stockA = 5
        # else stockA = 0 and that's already the default

        # price validation
        if GetBestVendor.validate_price(respA.price): # valid price, set it
            priceA = respA.price
        else: # discard it i.e. treat it as stock=0
            return NormalizedParams(stock=0, price=priceA, vendor_name=vname)
        
        # return the normalized params
        return NormalizedParams(stock=stockA, price=priceA, vendor_name=vname)
    
    @staticmethod
    def normalize_response_for_vendorB(resp: models.GenericVendorResponse) -> NormalizedParams:
        vname = Constants.VENDORB_NAME # vendor_name, declared as variable for easier reuse

        assert(resp.vendor_name == vname) # this will break if someone updates the code erroneously

        # default values
        stockB: int = 0
        priceB: float = 0

        # no retries implemented yet so stock treated as 0
        if resp.response_status == models.ResponseStatus.error: 
            return NormalizedParams(stock=stockB, price=priceB, vendor_name=vname)
        
        # logic specific to the response structure of vendorB
        # validate the response structure
        try:
            respB = models.VendorBResponse.model_validate(resp.response_body)
        except Exception as e:
            raise InvalidResponseStructure("Error validating the response body for vendorB: {}".format(e))

        # timestamp validation comes first to avoid any further delays
        if not GetBestVendor.is_timestamp_fresh(respB.last_refresh_time): # stale date => discard
            return NormalizedParams(stock=0, price=priceB, vendor_name=vname)
        
        # stock normalisation
        if (respB.inventory.product_inventory == 0 and respB.inventory.stock_status == models.VendorBStockStatus.in_stock): stockB = 5
        # else stockB = 0 and that's already the default

        # price validation
        if GetBestVendor.validate_price(respB.cost): # valid price, set it
            priceB = respB.cost
        else: # discard it i.e. treat it as stock=0
            return NormalizedParams(stock=0, price=priceB, vendor_name=vname)
        
        # return the normalized params
        return NormalizedParams(stock=stockB, price=priceB, vendor_name=vname)
    
    @staticmethod
    def normalize_response_for_vendorC(resp: models.GenericVendorResponse) -> NormalizedParams:
        vname = Constants.VENDORC_NAME # vendor_name, declared as variable for easier reuse

        assert(resp.vendor_name == vname) # this will break if someone updates the code erroneously

        # default values
        stockC: int = 0
        priceC: float = 0

        # no retries implemented yet so stock treated as 0
        if resp.response_status == models.ResponseStatus.error: 
            return NormalizedParams(stock=stockC, price=priceC, vendor_name=vname)
        
        # logic specific to the response structure of vendorC
        # validate the response structure
        try:
            respC = models.VendorCResponse.model_validate(resp.response_body)
        except Exception as e:
            raise InvalidResponseStructure("Error validating the response body for vendorC: {}".format(e))

        # timestamp validation comes first to avoid any further delays
        if not GetBestVendor.is_timestamp_fresh(respC.details_updated_at): # stale date => discard
            return NormalizedParams(stock=0, price=priceC, vendor_name=vname)
        
        # stock normalisation
        if (respC.details.p_inventory == 0 and respC.details.p_stock == models.VendorCStockStatus.in_stock): stockC = 5
        # else stockC = 0 and that's already the default

        # price validation
        if GetBestVendor.validate_price(respC.details.product_price): # valid price, set it
            priceC = respC.details.product_price
        else: # discard it i.e. treat it as stock=0
            return NormalizedParams(stock=0, price=priceC, vendor_name=vname)
        
        # return the normalized params
        return NormalizedParams(stock=stockC, price=priceC, vendor_name=vname)

    @staticmethod
    def get_normalized_parameters(result: models.GenericVendorResponse) -> NormalizedParams: # return namedtuple of (stock, price, vendor_name)
        match result.vendor_name: # if you add more vendors, then add the respective case here (one-time effort)
            case Constants.VENDORA_NAME:
                return GetBestVendor.normalize_response_for_vendorA(result)
            case Constants.VENDORB_NAME:
                return GetBestVendor.normalize_response_for_vendorB(result)
            case Constants.VENDORC_NAME:
                return GetBestVendor.normalize_response_for_vendorC(result)
            case _:
                raise InvalidVendorException("Vendor name doesn't exist!")

    @staticmethod
    def get_best_vendor(result_tuple: tuple[models.GenericVendorResponse, ...]) -> str:
        normalized_stock_price_list: list[NormalizedParams] = [] # list of (stock, price, vendor_name) tuples

        # iterate
        for result in result_tuple:
            normalized_stock_price_list.append(GetBestVendor.get_normalized_parameters(result))
        
        # get best vendor from the stock_price list
        return GetBestVendor.get_best_vendor_from_normalized_tuple_list(normalized_stock_price_list)