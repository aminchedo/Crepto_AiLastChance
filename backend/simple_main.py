import logging
import re
from contextlib import asynccontextmanager
from datetime import datetime

import structlog
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings
from security.input_validation import MarketRequest, TimeRangeRequest, PaginationRequest
from security.rate_limiter import rate_limit, MARKET_DATA_LIMIT, GENERAL_LIMIT
from security.jwt_auth import verify_token

# Security
security = HTTPBearer()

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
    yield
    # Shutdown
    logger.info("Shutting down Bolt AI Crypto API")


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


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get(f"{settings.API_PREFIX}/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get(f"{settings.API_PREFIX}/market/{{symbol}}")
@rate_limit(MARKET_DATA_LIMIT)
async def get_market_data(symbol: str, request: Request):
    """Get market data for a symbol."""
    # Validate symbol
    if not re.match(r'^[A-Z]{1,10}$', symbol):
        raise HTTPException(status_code=400, detail="Invalid symbol format")
    
    # Mock data for now
    return {
        "symbol": symbol.upper(),
        "price": 50000.0,
        "change_24h": 1000.0,
        "change_percent_24h": 2.0,
        "volume_24h": 1000000000,
        "market_cap": 1000000000000,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get(f"{settings.API_PREFIX}/market/{{symbol}}/history")
@rate_limit(MARKET_DATA_LIMIT)
async def get_price_history(symbol: str, request: Request, period: str = "1h"):
    """Get price history for a symbol."""
    # Validate inputs
    if not re.match(r'^[A-Z]{1,10}$', symbol):
        raise HTTPException(status_code=400, detail="Invalid symbol format")
    
    allowed_periods = ["1m", "5m", "15m", "1h", "4h", "1d", "1w"]
    if period not in allowed_periods:
        raise HTTPException(status_code=400, detail=f"Invalid period. Must be one of: {', '.join(allowed_periods)}")
    
    # Mock historical data
    return {
        "symbol": symbol.upper(),
        "period": period,
        "data": [
            {"timestamp": "2024-01-01T00:00:00Z", "open": 49000, "high": 51000, "low": 48000, "close": 50000, "volume": 1000000},
            {"timestamp": "2024-01-01T01:00:00Z", "open": 50000, "high": 52000, "low": 49000, "close": 51000, "volume": 1200000},
        ]
    }


@app.get(f"{settings.API_PREFIX}/news")
@rate_limit(GENERAL_LIMIT)
async def get_news(request: Request):
    """Get crypto news."""
    # Mock news data
    return {
        "articles": [
            {
                "id": "1",
                "title": "Bitcoin Reaches New All-Time High",
                "description": "Bitcoin has reached a new all-time high of $100,000",
                "url": "https://example.com/news/1",
                "publishedAt": "2024-01-01T12:00:00Z",
                "source": "CryptoNews",
                "sentiment": "positive"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "simple_main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
    )