
from app.adapters.vendorA_adapter import VendorAAdapter
from app.adapters.vendorB_adapter import VendorBAdapter
from app.factories.normalize_vendor_responses import VendorResponsesFactory
from app.switch.switch import VendorConstants

def register_all_vendors():
    VendorResponsesFactory.register(VendorConstants.VENDORA_NAME, VendorAAdapter())
    VendorResponsesFactory.register(VendorConstants.VENDORB_NAME, VendorBAdapter())