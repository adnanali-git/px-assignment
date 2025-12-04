from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds", # <-- counter name on prometheus
    "Latency of HTTP requests",     # <-- Human readable label
    ["method", "endpoint"]          # <-- parameters to track
)

VENDOR_FAILURES = Counter(
    "vendor_failures_total",
    "Number of failed vendor requests",
    ["vendor"]
)

VENDOR_LATENCY = Histogram(
    "vendor_latency_seconds",
    "Latency of vendor requests",
    ["vendor"]
)

