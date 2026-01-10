
class Constants:

    BEST_VENDOR_SELECTION_OOS_MESSAGE = "OUT_OF_STOCK"

    """
    even these can be customised (different timeout and retry-policy for different vendors)
    the same way the RL and CB configs are customised
    """
    # move to .env ??
    VENDOR_API_TIMEOUT = 2.0 # in seconds
    VENDOR_API_RETRIES = 2
    DELAY_BETWEEN_RETRIES = 1 # in seconds, skipping exponential-backoff for now to keep things simple. modifications are minimal if it's needed

    # data freshness limit, beyond which it is to be discarded
    FRESHNESS_LIMIT = 600 # in seconds