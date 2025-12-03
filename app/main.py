"""FastAPI application entrypoint."""
import logging
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import health, repo

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Create FastAPI app
# Disable docs in production for security and reduced overhead
# GAE_ENV is set to 'standard' in production GAE environment
is_production = os.getenv("GAE_ENV", "").startswith("standard")

app = FastAPI(
    title="Project Designer GAE API",
    description="Minimal HTTP API service",
    version="1.0.0",
    # Disable docs in production GAE, keep for local dev
    docs_url="/docs" if not is_production else None,
    redoc_url="/redoc" if not is_production else None,
    # Disable OpenAPI schema in production to reduce overhead
    openapi_url="/openapi.json" if not is_production else None,
)


# Include routers
app.include_router(health.router)
app.include_router(repo.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests and responses."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code}")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to ensure JSON error responses."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "GAE API",
        "status": "ok",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs" if not is_production else "disabled"
        }
    }
