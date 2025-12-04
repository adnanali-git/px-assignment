from asyncio import gather as asyncio_gather
from fastapi import Depends
from redis.asyncio import Redis
from typing import NamedTuple
from time import time_ns

import app.schemas.vendor.models as models
from app.core.constants import Constants
from app.switch.switch import SwitchValues
from app.services.cache_service import get_best_vendor_for_sku_from_redis, set_best_vendor_for_sku_in_redis

class InvalidResponseStructure(Exception):
    pass

class InvalidVendorException(Exception):
    pass

class NormalizedParams(NamedTuple):
    stock: int
    price: float
    vendor_name: str

from app.external_clients.vendors import VendorClient

class SKUServiceHelper:
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

        # check if only one vendor in the list, then simply return that vendor's name
        if len(iter1) == 1: return iter1[0].vendor_name

        # len(iter1) is guaranteed to be atleast 2 beyond this point
        # else proceed to further filtering
        if not SwitchValues.IS_PRICE_STOCK_RULE_UPGRADE_ENABLED: # if rule_upgrade not enabled, use the default rule
            # sort asc by price, if tie then sort desc by stock hence minus sign
            best_vendor = sorted(iter1, key=lambda tup: (tup.price, -tup.stock))[0].vendor_name
            return best_vendor
        else:
            # step-1: sort same as above
            iter1.sort(key=lambda tup: (tup.price, -tup.stock))
            best_vendor = iter1[0] # best vendor so far

            # step-2: compare two vendors for the price-diff one-by-one
            curr_vendor = iter1[1] # declared outside loop to avoid scoping issues
            for idx in range(1, len(iter1)): # generic code to future-proof for further vendor additions
                curr_vendor = iter1[idx] # the vendor to be compared with
                # compare price diff
                pA = best_vendor.price
                pB = curr_vendor.price # pB is by definition more than pA due to the way we sorted the list
                if pA * 1.1 < pB: # diff is more than 10%
                    if curr_vendor.stock > best_vendor.stock: # set curr_vendor as best_vendor
                        best_vendor = curr_vendor
                    # else: no change in best_vendor
                # else: no change in best_vendor
            
            # return best after all the comparisons
            return best_vendor.vendor_name

    @staticmethod
    def validate_price(price: float) -> bool:
        try:
            float(price) # price must be numeric
            return (price > 0) # price must be > 0
        except ValueError:
            return False

    @staticmethod
    def normalize_response_for_vendorA(resp: models.GenericVendorResponse) -> NormalizedParams:
        vname = Constants.VENDORA_NAME # vendor_name, declared as variable for easier reuse

        assert(resp.vendor_name == vname) # this will break if someone updates the code erroneously

        # default values
        stockA: int = 0
        priceA: float = 0

        # Error is treated as stock=0, can modify it to do smth else if needed
        if resp.response_status == models.ResponseStatus.error: 
            return NormalizedParams(stock=stockA, price=priceA, vendor_name=vname)
        
        # logic specific to the response structure of vendorA
        # validate the response structure
        try:
            respA = models.VendorAResponse.model_validate(resp.response_body)
        except Exception as e:
            raise InvalidResponseStructure("Error validating the response body for vendorA: {}".format(e))

        # timestamp validation comes first to avoid any further delays
        if not SKUServiceHelper.is_timestamp_fresh(respA.last_updated): # stale date => discard
            return NormalizedParams(stock=0, price=priceA, vendor_name=vname)
        
        # stock normalisation
        if (respA.inventory == 0 and respA.product_in_stock): stockA = 5
        # else stockA = 0 and that's already the default

        # price validation
        if SKUServiceHelper.validate_price(respA.price): # valid price, set it
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
        if not SKUServiceHelper.is_timestamp_fresh(respB.last_refresh_time): # stale date => discard
            return NormalizedParams(stock=0, price=priceB, vendor_name=vname)
        
        # stock normalisation
        if (respB.inventory.product_inventory == 0 and respB.inventory.stock_status == models.VendorBStockStatus.in_stock): stockB = 5
        # else stockB = 0 and that's already the default

        # price validation
        if SKUServiceHelper.validate_price(respB.cost): # valid price, set it
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
        if not SKUServiceHelper.is_timestamp_fresh(respC.details_updated_at): # stale date => discard
            return NormalizedParams(stock=0, price=priceC, vendor_name=vname)
        
        # stock normalisation
        if (respC.details.p_inventory == 0 and respC.details.p_stock == models.VendorCStockStatus.in_stock): stockC = 5
        # else stockC = 0 and that's already the default

        # price validation
        if SKUServiceHelper.validate_price(respC.details.product_price): # valid price, set it
            priceC = respC.details.product_price
        else: # discard it i.e. treat it as stock=0
            return NormalizedParams(stock=0, price=priceC, vendor_name=vname)
        
        # return the normalized params
        return NormalizedParams(stock=stockC, price=priceC, vendor_name=vname)

    @staticmethod
    def get_normalized_parameters(result: models.GenericVendorResponse) -> NormalizedParams: # return namedtuple of (stock, price, vendor_name)
        match result.vendor_name: # if you add more vendors, then add the respective case here (one-time effort)
            case Constants.VENDORA_NAME:
                return SKUServiceHelper.normalize_response_for_vendorA(result)
            case Constants.VENDORB_NAME:
                return SKUServiceHelper.normalize_response_for_vendorB(result)
            case Constants.VENDORC_NAME:
                return SKUServiceHelper.normalize_response_for_vendorC(result)
            case _:
                raise InvalidVendorException("Vendor name doesn't exist!")

    @staticmethod
    def get_best_vendor(result_tuple: tuple[models.GenericVendorResponse, ...]) -> str:
        normalized_stock_price_list: list[NormalizedParams] = [] # list of (stock, price, vendor_name) tuples

        # iterate
        for result in result_tuple:
            normalized_stock_price_list.append(SKUServiceHelper.get_normalized_parameters(result))
        
        # get best vendor from the stock_price list
        return SKUServiceHelper.get_best_vendor_from_normalized_tuple_list(normalized_stock_price_list)

# the business logic resides here
class SKUService:
    def __init__(self):
        self.vendor_client = VendorClient()

    async def get_best_vendor_for_sku(self, sku: str, redis_client: Redis) -> str:

        # Step 1: Find best vendor in cache_service and return
        # Check Redis cache
        best_vendor = await get_best_vendor_for_sku_from_redis(redis_client, sku)
        if best_vendor:
            # print("Accessed cache")
            return best_vendor

        # this block is now more generic after introducing "Any" type for the "response_body" field
        # so no extra code changes required (unlike before) if the order of vendors is altered or new
        # vendors added

        # Step 2: If not found fetch via API call
        results = await asyncio_gather(
            self.vendor_client.call_vendorA(sku), 
            self.vendor_client.call_vendorB(sku),
            self.vendor_client.call_vendorC(sku),
            # return_exceptions=True, # to run all tasks to completion, even if some raise exceptions 
        )

        # the business logic to apply over the results[] tuple
        best_vendor = SKUServiceHelper.get_best_vendor(results)

        # Store in Redis cache with default ttl
        await set_best_vendor_for_sku_in_redis(redis_client, sku, best_vendor)

        return best_vendor
