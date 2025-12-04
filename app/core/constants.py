
class Constants:
    VENDORA_NAME = "vendorA"
    VENDORA_ENDPOINT = "https://mocki.io/v1/e7517f58-f058-4208-bad7-9754ddf6e84b"

    VENDORB_NAME = "vendorB"
    VENDORB_ENDPOINT = "https://mocki.io/v1/243fab59-56dd-4315-a424-fa51e6983009"

    VENDORC_NAME = "vendorC"
    VENDORC_ENDPOINT = "https://mocki.io/v1/e7517f58-f058-4208-bad7-9754ddf6e84x"

    BEST_VENDOR_SELECTION_OOS_MESSAGE = "OUT_OF_STOCK"

    # move to .env ??
    VENDOR_API_TIMEOUT = 2.0 # in seconds
    VENDOR_API_RETRIES = 2
    DELAY_BETWEEN_RETRIES = 1 # in seconds, skipping exponential-backoff for now to keep things simple. modifications are minimal if it's needed

    # data freshness limit, beyond which it is to be discarded
    FRESHNESS_LIMIT = 600 # in seconds