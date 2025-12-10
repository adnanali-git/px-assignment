
from typing import NamedTuple

class SwitchValues:
    # could be moved to .env file at first thought but upon further thinking 
    # one realises that it doesn't matter since this variable is only due to
    # the simulation/mocking requirement in this task. It doesn't arise in a
    # real-life production codebase.
    IS_MOCKING_VIA_FILE: bool = True 
    IS_PRICE_STOCK_RULE_UPGRADE_ENABLED: bool = True

class VendorConstants:
    VENDORA_NAME = "vendorA"
    VENDORB_NAME = "vendorB"
    VENDORC_NAME = "vendorC"

    VENDOR_ENDPOINTS = {
        VENDORA_NAME: "https://mocki.io/v1/e7517f58-f058-4208-bad7-9754ddf6e84b",
        VENDORB_NAME: "https://mocki.io/v1/243fab59-56dd-4315-a424-fa51e6983009",
        VENDORC_NAME: "https://mocki.io/v1/e7517f58-f058-4208-bad7-9754ddf6e84x"
    }

# for the class below
class CBConfig(NamedTuple):
    max_fail: int       # after these many failures, open the circuit
    open_duration: int  # in seconds

# ideally put in a switch microservice outside this codebase
# so that it can be swiftly altered in emergency scenarios saving
# the time needed to push new code just for modifying these values and then redeploying it
class CircuitBreakerParams:
    """
    Vendor not found in the dict => No CB enabled for the vendor
    """
    CB_CONFIG_FOR_VENDORS = { # dict_structure = <vendor_name>: <CBConfig() tuple>
        VendorConstants.VENDORC_NAME: CBConfig(max_fail=3, open_duration=30)
    }

# for the class below
class RLConfig(NamedTuple):
    window_in_millis: int
    requests: int         # limit per window

# all ratelimit related flags here
class RateLimitParams:
    """
    When adding a new vendor: if you want to rate-limit it, add the config here
    -> If we don't need this level of generalization, use common values (i.e. a single
    value used by all clients like the last two lines in this class definition)
    -> Or don't add it here and modify the fallback behavior if vendor_name not in 
    the dict, to fallback to either default global values or no RL enabled for client.
    """
    RL_CONFIG_FOR_VENDORS = { # dict_structure = <vendor_name>: <RLConfig() tuple>
        VendorConstants.VENDORA_NAME: RLConfig(window_in_millis=60_000, requests=60), 
        VendorConstants.VENDORB_NAME: RLConfig(window_in_millis=60_000, requests=60),
        VendorConstants.VENDORC_NAME: RLConfig(window_in_millis=60_000, requests=60)
    }
    # GLOBAL_WINDOW_IN_MILLIS = 60_000 # in millis
    # GLOBAL_REQUEST_LIMIT = 60 # per window

# as the name suggests, can be moved to a private vault in production env
# this is mere simulation
class PrivateVault:
    """
    Vendor not found in the dict => no api_key needed when calling the vendor
    """
    API_KEY_FOR_VENDORS = { # dict_structure = <vendor_name>: <api_key>
        VendorConstants.VENDORA_NAME: "api-key-for-vendorA", 
        VendorConstants.VENDORB_NAME: "api-key-for-vendorB",
        VendorConstants.VENDORC_NAME: "api-key-for-vendorC"
    }
