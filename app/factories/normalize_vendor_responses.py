
from app.adapters.base_adapter import BaseAdapter
from app.adapters.vendorA_adapter import VendorAAdapter
from app.adapters.vendorB_adapter import VendorBAdapter
from app.switch.switch import VendorConstants

class VendorResponsesFactory:
    
    def get_vendor(self, name: str) -> BaseAdapter:
        """
        A simple function to get adapter method based on vendor_name, 
        good if vendors are few and don't change frequently  
        as the if-chain won't scale for a large number of vendors
        """
        if name == VendorConstants.VENDORA_NAME: return VendorAAdapter()
        else: return VendorBAdapter()


    