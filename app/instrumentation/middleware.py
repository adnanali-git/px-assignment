import time
from fastapi import Request, Response
from .metrics import REQUEST_COUNT, REQUEST_LATENCY

async def prometheus_middleware(request: Request, call_next):
    start = time.time()
    response: Response = await call_next(request)

    processing_time = time.time() - start
    method = request.method
    endpoint = request.url.path
    status = response.status_code

    REQUEST_LATENCY.labels(method, endpoint).observe(processing_time)
    REQUEST_COUNT.labels(method, endpoint, status).inc()

    return response
