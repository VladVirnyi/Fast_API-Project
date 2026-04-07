"""FastAPI main module with PostgreSQL integration."""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import get_settings
from app.routers import user, category, product, order, profile
import uvicorn

settings = get_settings()

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

# Register routers
app.include_router(user.router)
app.include_router(category.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(profile.router)


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


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
