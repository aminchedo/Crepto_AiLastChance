import asyncio
from datetime import datetime
from typing import Dict, Optional

from db.database import engine
from db.redis_client import redis_client
from fastapi import APIRouter, status
from pydantic import BaseModel

from config import settings

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    checks: Dict[str, str]


class ReadinessResponse(BaseModel):
    ready: bool
    checks: Dict[str, bool]


class LivenessResponse(BaseModel):
    alive: bool


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.
    Returns overall system health status.
    """
    checks = {}
    overall_status = "healthy"

    # Check database
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
        overall_status = "degraded"

    # Check Redis
    try:
        if redis_client.redis:
            await redis_client.redis.ping()
            checks["redis"] = "healthy"
        else:
            checks["redis"] = "not connected"
            overall_status = "degraded"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"
        overall_status = "degraded"

    return {
        "status": overall_status,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
    }


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness_check():
    """
    Readiness check - determines if the service can accept traffic.
    Used by Kubernetes/load balancers to know when to route traffic.
    """
    checks = {}

    # Check database connection
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        checks["database"] = True
    except Exception:
        checks["database"] = False

    # Check Redis connection
    try:
        if redis_client.redis:
            await redis_client.redis.ping()
            checks["redis"] = True
        else:
            checks["redis"] = False
    except Exception:
        checks["redis"] = False

    # Service is ready only if all checks pass
    ready = all(checks.values())

    return {"ready": ready, "checks": checks}


@router.get("/health/live", response_model=LivenessResponse)
async def liveness_check():
    """
    Liveness check - determines if the service is alive.
    Used by Kubernetes to know when to restart the container.
    This should be a simple check that always succeeds if the app is running.
    """
    return {"alive": True}


@router.get("/health/startup")
async def startup_check():
    """
    Startup check - determines if the service has finished starting up.
    Used by Kubernetes to know when the container is ready to accept traffic.
    """
    # Check if critical components are initialized
    checks = {}

    try:
        # Check database
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        checks["database"] = True
    except Exception:
        checks["database"] = False
        return {"started": False, "checks": checks}

    try:
        # Check Redis
        if redis_client.redis:
            await redis_client.redis.ping()
            checks["redis"] = True
        else:
            checks["redis"] = False
            return {"started": False, "checks": checks}
    except Exception:
        checks["redis"] = False
        return {"started": False, "checks": checks}

    return {"started": True, "checks": checks}
