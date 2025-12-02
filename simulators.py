import models
from jsonpickle import encode
from random import uniform, choices, randint
from string import ascii_letters, digits, punctuation

# all helper functions under this class
class HelperFuncs:
    @staticmethod
    def gen_rand_string(length: int, charset: str) -> str:
        # return a string of length "length" (value for param k) from given charset
        return "".join(choices(charset, k=length))

# bounds for random generation
class Constants:
    MIN_PRICE: float = 100.0
    MAX_PRICE: float = 2000.0

    CHARSET: str = "".join((" ", ascii_letters, digits, punctuation))
    PRODUCT_NAME_MIN: int = 3
    PRODUCT_NAME_MAX: int = 20
    PRODUCT_DESCRIPTION_MIN: int = 0
    PRODUCT_DESCRIPTION_MAX: int = 200

    MAX_STOCK: int = 100

# simulator for vendorA
class SimulatorA:
    # declare respA with filler values to have a valid definition
    respA: models.VendorAResponse = models.VendorAResponse(
        product_id="",
        product_name="",
        price=0,
        inventory=None,
        product_in_stock=False
    )
    # file path for external access
    mock_file_path: str = "./simulated_responses/vendorA_resp.json"

    def __init__(self, sku: str):
        # set sku
        self.respA.product_id = sku
        # set product name
        self.respA.product_name = HelperFuncs.gen_rand_string(
            randint(Constants.PRODUCT_NAME_MIN, Constants.PRODUCT_NAME_MAX),
            Constants.CHARSET
        )
        # set product description
        switch_on = randint(0, 1) # randomly select between a randomly generated description or None
        if switch_on: # then set a description
            self.respA.product_description = HelperFuncs.gen_rand_string(
            randint(Constants.PRODUCT_DESCRIPTION_MIN, Constants.PRODUCT_DESCRIPTION_MAX),
            Constants.CHARSET
        )
        else: # else None
            self.respA.product_description = None
        
        # set price to a randomly generated float
        self.respA.price = uniform(Constants.MIN_PRICE, Constants.MAX_PRICE)

        # set inventory & stock_status
        switch_on = randint(0, 1)
        if switch_on: # then stock = 5
            self.respA.inventory = 0 if randint(0, 1) else None
            self.respA.product_in_stock = True
        else:
            switch_on = randint(0, 1)
            if switch_on: # in_stock = True
                self.respA.product_in_stock = True
                self.respA.inventory = randint(1, Constants.MAX_STOCK) # cannot be 0 to avoid above case
            else: 
                self.respA.product_in_stock = False
                self.respA.inventory = randint(0, Constants.MAX_STOCK) # can be 0

        '''
        [TODO] If time allows: 
        POST call https://api.mocki.io/public/mocks with this payload and other headers
        and receive "slug" and "url" and set VendorURL = url
        '''

        # write to file
        with open(self.mock_file_path, "w") as mock_file:
            mock_file.write(encode(self.respA))
        mock_file.close()

# simulator for vendorB
class SimulatorB: 
    # declare respB with filler values to have a valid definition
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
        )
    )
    # file path for external access
    mock_file_path: str = "./simulated_responses/vendorB_resp.json"

    def __init__(self, sku: str):
        # set sku
        self.respB.id = sku
        # set product name
        self.respB.product_metadata.title = HelperFuncs.gen_rand_string(
            randint(Constants.PRODUCT_NAME_MIN, Constants.PRODUCT_NAME_MAX),
            Constants.CHARSET
        )
        # set product description
        switch_on = randint(0, 1) # randomly select between a randomly generated description or empty string
        if switch_on: # then set a description
            self.respB.product_metadata.description = HelperFuncs.gen_rand_string(
            randint(Constants.PRODUCT_DESCRIPTION_MIN, Constants.PRODUCT_DESCRIPTION_MAX),
            Constants.CHARSET
        )
        else: # else None
            self.respB.product_metadata.description = ""
        
        # set image details as empty for now
        self.respB.product_metadata.image_details = ""
        
        # set price to a randomly generated float
        self.respB.cost = uniform(Constants.MIN_PRICE, Constants.MAX_PRICE)

        # set inventory & stock_status
        switch_on = randint(0, 1)
        if switch_on: # then stock = 5
            self.respB.inventory.product_inventory = 0
            self.respB.inventory.stock_status = models.VendorBStockStatus.in_stock
        else:
            switch_on = randint(0, 1)
            if switch_on: # in_stock = True
                self.respB.inventory.stock_status = models.VendorBStockStatus.in_stock
                self.respB.inventory.product_inventory = randint(1, Constants.MAX_STOCK) # cannot be 0 to avoid above case
            else: 
                self.respB.inventory.stock_status = models.VendorBStockStatus.out_of_stock
                self.respB.inventory.product_inventory = randint(0, Constants.MAX_STOCK) # can be 0

        '''
        [TODO] If time allows: 
        POST call https://api.mocki.io/public/mocks with this payload and other headers
        and receive "slug" and "url" and set VendorURL = url
        '''

        # write to file
        with open(self.mock_file_path, "w") as mock_file:
            mock_file.write(encode(self.respB))
        mock_file.close()

# simulator for vendorC
class SimulatorC: 
    # declare respC with filler values to have a valid definition
    respC: models.VendorCResponse = models.VendorCResponse(
        sku_id="",
        details=models.VendorCDetails(
            name="",
            desc="",
            product_price=0,
            p_inventory=0,
            p_stock=models.VendorCStockStatus.out_of_stock
        )
    )
    # file path for external access
    mock_file_path: str = "./simulated_responses/vendorC_resp.json"

    def __init__(self, sku: str):
        # set sku
        self.respC.sku_id = sku
        # set product name
        self.respC.details.name = HelperFuncs.gen_rand_string(
            randint(Constants.PRODUCT_NAME_MIN, Constants.PRODUCT_NAME_MAX),
            Constants.CHARSET
        )
        # set product description
        switch_on = randint(0, 1) # randomly select between a randomly generated description or empty string
        if switch_on: # then set a description
            self.respC.details.desc = HelperFuncs.gen_rand_string(
            randint(Constants.PRODUCT_DESCRIPTION_MIN, Constants.PRODUCT_DESCRIPTION_MAX),
            Constants.CHARSET
        )
        else: # else None
            self.respC.details.desc = ""
        
        # set price to a randomly generated float
        self.respC.details.product_price = uniform(Constants.MIN_PRICE, Constants.MAX_PRICE)

        # set inventory & stock_status
        switch_on = randint(0, 1)
        if switch_on: # then stock = 5
            self.respC.details.p_inventory = 0
            self.respC.details.p_stock = models.VendorCStockStatus.in_stock
        else:
            switch_on = randint(0, 1)
            if switch_on: # in_stock = True
                self.respC.details.p_stock = models.VendorCStockStatus.in_stock
                self.respC.details.p_inventory = randint(1, Constants.MAX_STOCK) # cannot be 0 to avoid above case
            else: 
                self.respC.details.p_stock = models.VendorCStockStatus.out_of_stock
                self.respC.details.p_inventory = randint(0, Constants.MAX_STOCK) # can be 0

        '''
        [TODO] If time allows: 
        POST call https://api.mocki.io/public/mocks with this payload and other headers
        and receive "slug" and "url" and set VendorURL = url
        '''

        # write to file
        with open(self.mock_file_path, "w") as mock_file:
            mock_file.write(encode(self.respC))
        mock_file.close()