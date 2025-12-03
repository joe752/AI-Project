"""FastAPI application entrypoint."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import health, repo
from app import rube_client as rube_module

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup: Initialize Rube client
    logger.info(f"Starting GAE API service")
    logger.info(f"Rube base URL: {settings.rube_base_url}")
    logger.info(f"Log level: {settings.log_level}")

    try:
        rube_module.rube_client = rube_module.RubeClient()
        logger.info("RubeClient initialized successfully")
    except RuntimeError as exc:
        logger.error(f"Failed to initialize RubeClient: {exc}")
        raise

    yield

    # Shutdown: Clean up resources
    logger.info("Shutting down GAE API service")
    if rube_module.rube_client:
        await rube_module.rube_client.close()


# Create FastAPI app
app = FastAPI(
    title="Project Designer GAE API",
    description="HTTP API for repository inspection via Rube",
    version="1.0.0",
    lifespan=lifespan
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
        "service": "Project Designer GAE API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
