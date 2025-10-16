import logging
from contextlib import asynccontextmanager

import structlog
from api import (admin, alerts, auth, export, market, monitoring, predictions,
                 proxy, signals, websocket)
from db.database import close_db, init_db
from db.redis_client import redis_client
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from monitoring import health, metrics

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Bolt AI Crypto API", version=settings.APP_VERSION)

    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")

        # Initialize Redis (optional for development)
        try:
            await redis_client.connect()
            logger.info("Redis connected")
        except Exception as redis_error:
            logger.warning("Redis connection failed, continuing without Redis", error=str(redis_error))

    except Exception as e:
        logger.error("Startup failed", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("Shutting down Bolt AI Crypto API")
    await close_db()
    try:
        await redis_client.disconnect()
    except Exception:
        pass  # Redis might not be connected


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Cryptocurrency Trading Dashboard API",
    lifespan=lifespan,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "X-JSON-Response", "Authorization"],
    max_age=600,
)

# Include routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(market.router, prefix=settings.API_PREFIX)
app.include_router(predictions.router, prefix=settings.API_PREFIX)
app.include_router(signals.router, prefix=settings.API_PREFIX)
app.include_router(alerts.router, prefix=settings.API_PREFIX)
app.include_router(websocket.router, prefix=settings.API_PREFIX)
app.include_router(admin.router, prefix=settings.API_PREFIX)
app.include_router(monitoring.router, prefix=settings.API_PREFIX)
app.include_router(export.router, prefix=settings.API_PREFIX)
app.include_router(proxy.router, prefix=settings.API_PREFIX)  # API Proxy for CORS-free external calls
app.include_router(health.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    if settings.PROMETHEUS_ENABLED:
        return await metrics.get_metrics()
    return {"error": "Metrics disabled"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
    )