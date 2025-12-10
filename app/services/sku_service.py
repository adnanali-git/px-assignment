from asyncio import gather as asyncio_gather
from redis.asyncio import Redis
from typing import NamedTuple
from time import time_ns

from app.external_clients import vendorA, vendorB
from app.factories.normalize_vendor_responses import VendorResponsesFactory
import app.schemas.vendor.models as models
from app.core.constants import Constants
from app.switch.switch import SwitchValues
import app.services.cache_service as CacheService

class NormalizedParams(NamedTuple):
    stock: int
    price: float
    vendor_name: str

class SKUServiceHelper:
    @staticmethod
    def _is_timestamp_fresh(timestamp: int) -> bool:
        """
        Business logic to check for timestamp freshness
        """
        if (time_ns() - timestamp * 1_000_000) > Constants.FRESHNESS_LIMIT * 1_000_000_000:
            return False
        return True
    
    @staticmethod
    def _validate_price(price: float) -> bool:
        """
        Validate price based on business rules
        """
        return (price > 0) # price must be > 0
        
        # float checking happens automatically in the http-response-validation in the external-client call
        # so no need for this block
        # try:
        #     # float(price) # price must be numeric
        #     # return (price > 0) # price must be > 0
        # except ValueError:
        #     return False

    @staticmethod
    def convert_normalized_vendor_response_to_normalized_params(n_res: models.NormalizedVendorResponse) -> NormalizedParams | None:
        """
        Business logic to use fields like "stock_status", "inventory", and freshness timestamp to 
           (i) discard invalid entries (invalid or not decided by the business logic)
           (ii) return a slim response holding only 3 params: vendor_name, stock and price
        
        Helps separate the processing logic from the final-decision logic
        """

        # default values
        stock: int = 0
        price: float = -1

        # timestamp validation comes first to avoid any further delays
        if not SKUServiceHelper._is_timestamp_fresh(n_res.last_updated): # stale date => discard
            return None
        
        # stock normalisation
        if (n_res.inventory == 0 and n_res.stock_status): stock = 5
        # else stockA = 0 and that's already the default

        # price validation
        if SKUServiceHelper._validate_price(n_res.price): # valid price, set it
            price = n_res.price
        else: # discard it
            return None
        
        # return the normalized params
        return NormalizedParams(stock=stock, price=price, vendor_name=n_res.vendor_name)
    
    @staticmethod
    def stock_price_decider(normalized_tuple_list: list[NormalizedParams]) -> str:
        """
        Given a tuple of NormalizedParams, select the best vendor based on the tuple-params and the business logic
        """

        # drop all tuples with stock = 0 (assuming this line runs fine for an empty list)
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

class SKUService:
    """
    Business logic resides here
    """
    def _process_normalized_vendor_response(self, n_res_tup: tuple[models.NormalizedVendorResponse, ...]) -> list[NormalizedParams]:
        """
        Trim down tuple of NormalizedVendorResponse into tuple of NormalizedParams of only 3 params
        """
        output: list[NormalizedParams] = []

        # return empty tuple as output if input is empty
        if not len(n_res_tup): return output

        # else process
        for n_res in n_res_tup:
            # process_response
            p_res = SKUServiceHelper.convert_normalized_vendor_response_to_normalized_params(n_res)
            if p_res: # i.e. not None
                output.append(p_res)
        
        return output
    
    def _normalize_responses(self, res_tup: tuple[models.GenericVendorResponse, ...]) -> tuple[models.NormalizedVendorResponse, ...]:
        """
        Get the right adapter-class based on vendor_name, normalize it and return
        """
        # return empty tuple as output if input is empty
        default_tup = tuple[models.NormalizedVendorResponse]()
        if not len(res_tup): return default_tup

        return tuple((
            VendorResponsesFactory().get_vendor(res.vendor_name).normalize(res.response_body) for res in res_tup
        )) # the tuple() wrapping should not be required iirc but putting it there just in case
    
    def _handle_errored_responses(self, res_tup: tuple[models.GenericVendorResponse, ...]) -> tuple[models.GenericVendorResponse, ...]:
        """
        Business logic to deal with vendor responses that failed (HttpException, ValidationError or others)
        """
        # my assumption since it's not mentioned: just discard it
        return tuple((
            res for res in res_tup if res.response_status == models.ResponseStatus.success
        )) # the tuple() wrapping should not be required iirc but putting it there just in case

    # call all vendors async
    async def _fetch_all_async(self, sku: str, redis_client: Redis) -> tuple[models.GenericVendorResponse, ...]:
        # this block is now more generic after introducing "Any" type for the "response_body" field
        # so no extra code changes required (unlike before) if the order of vendors is altered or new
        # vendors added
        return await asyncio_gather(
            vendorA.call_vendor(sku, redis_client), 
            vendorB.call_vendor(sku, redis_client),
            # return_exceptions=True, # to run all tasks to completion, even if some raise exceptions 
        )

    async def get_best_vendor_for_sku(self, sku: str, redis_client: Redis) -> str:

        # Step 1: Find best vendor in cache_service and return
        # Check Redis cache
        best_vendor = await CacheService.get_best_vendor_for_sku_from_redis(redis_client, sku)
        if best_vendor:
            # print("Accessed cache")
            return best_vendor

        # Step 2: If not found fetch via API call
        results = self._fetch_all_async(sku, redis_client)

        # Step 3: deal with errored-out responses here before going to adapter layer, 
        # because that's owned by this layer not the adapter
        results_post_error_handling = self._handle_errored_responses(results)

        # Step 4: Normalize the remaining results to a uniform resp structure
        normalized_results = self._normalize_responses(results_post_error_handling)

        # Step 5: Trim down response to NormalizedParams tuple with only 3 params
        trimmed_results = self._process_normalized_vendor_response(normalized_results)

        # Step 6: Get best vendor from the final trimmed_results tuple
        best_vendor = SKUServiceHelper.stock_price_decider(trimmed_results)

        # Store in Redis cache with default ttl
        await CacheService.set_best_vendor_for_sku_in_redis(redis_client, sku, best_vendor)

        return best_vendor
