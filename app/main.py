from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from app.core.lifespan_events import app_lifespan
from app.instrumentation.middleware import prometheus_middleware
from app.routers.sku import router as sku_router # your routers

app = FastAPI(lifespan=app_lifespan)

# ---- Register Middleware ----
app.middleware("http")(prometheus_middleware)

# ---- Routers ----
app.include_router(sku_router)

# ---- Prometheus Endpoint ----
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)