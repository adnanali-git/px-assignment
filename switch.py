
class SwitchValues:
    # could be moved to .env file at first thought but upon further thinking 
    # one realises that it doesn't matter since this variable is only due to
    # the simulation/mocking requirement in this task. It doesn't arise in a
    # real-life production codebase.
    IS_MOCKING_VIA_FILE: bool = True 
    IS_PRICE_STOCK_RULE_UPGRADE_ENABLED: bool = True
    RATE_LIMIT_FOR_VENDORS_ENABLED: bool = True

# ideally put in a switch microservice outside this codebase
# so that it can be swiftly altered in emergency scenarios saving
# the time needed to push new code just for modifying these values and then redeploying it
class CircuitBreakerParams:
    # params for vendorC
    VENDORC_CB_MAX_FAIL = 3 # after these many failures, open the circuit
    VENDORC_CB_OPEN_DURATION = 30 # in seconds

# as the name suggests, can be moved to a private vault in production env
# this is mere simulation
class PrivateVault:
    API_KEY_FOR_VENDORA = "api-key-for-vendorA"
    API_KEY_FOR_VENDORB = "api-key-for-vendorB"
    API_KEY_FOR_VENDORC = "api-key-for-vendorC"
