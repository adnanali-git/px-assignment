
from app.adapters.base_adapter import BaseAdapter

class VendorResponsesFactory:
    _registry: dict[str, BaseAdapter] = {}

    @classmethod
    def register(cls, key: str, client_cls: BaseAdapter):
        cls._registry[key] = client_cls

    @classmethod
    def get_vendor(cls, key: str) -> BaseAdapter:
        """
        A simple function to get adapter method based on vendor_name, 
        if-chain: good if vendors are few and don't change frequently  
        registry-factory: scale for a large number of vendors
        """
        if key not in cls._registry:
            raise ValueError(f"Unknown vendor '{key}'")
        return cls._registry[key]