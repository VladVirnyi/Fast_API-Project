"""FastAPI main module with PostgreSQL integration."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import Counter, Gauge
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import get_settings
from app.routers import auth, category, order, product, profile, user

import uvicorn

settings = get_settings()

ENTITIES_CREATED_TOTAL = Counter(
    "app_entities_created_total",
    "Total number of entities created",
)
TOTAL_PURCHASE_VALUE = Gauge(
    "app_total_purchase_value",
    "Total value of processed purchases",
)
ROOT_HITS_TOTAL = Counter(
    "app_root_hits_total",
    "Total number of hits to root endpoint",
)
HEALTH_HITS_TOTAL = Counter(
    "app_health_hits_total",
    "Total number of hits to health endpoint",
)
DOCS_HITS_TOTAL = Counter(
    "app_docs_hits_total",
    "Total number of hits to docs endpoint",
)

# Startup/shutdown lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    print("🚀 API startup complete")
    
    yield
    
    # Shutdown
    print("🛑 Application shutdown...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)


@app.middleware("http")
async def endpoint_hit_metrics(request, call_next):
    """Count hits for a small set of endpoints."""
    if request.url.path == "/":
        ROOT_HITS_TOTAL.inc()
    elif request.url.path == "/health":
        HEALTH_HITS_TOTAL.inc()
    elif request.url.path == "/docs":
        DOCS_HITS_TOTAL.inc()
    return await call_next(request)

# Register routers
app.include_router(user.router)
app.include_router(category.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(profile.router)
app.include_router(auth.router)


@app.get("/")
async def root():
    """Main API endpoint."""
    return {
        "message": "Welcome to FastAPI",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/health")
async def health_check():
    """Application health check."""
    return {"status": "healthy"}


@app.post("/metrics/demo/entity")
async def metrics_demo_entity_created():
    """Increment demo entity counter."""
    ENTITIES_CREATED_TOTAL.inc()
    return {"status": "ok"}


@app.post("/metrics/demo/total_value")
async def metrics_demo_total_value(amount: float):
    """Increment demo total purchase value."""
    TOTAL_PURCHASE_VALUE.inc(amount)
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
