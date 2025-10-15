from datetime import datetime, timedelta
from typing import List, Optional

from api.deps import get_current_user
from db.database import get_db
from db.redis_client import redis_client
from fastapi import APIRouter, Depends, HTTPException, Query
from models.user import User
from schemas.market import (CandlestickResponse, MarketDataResponse,
                            TechnicalIndicatorsResponse)
from services.market_service import MarketService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/market", tags=["Market Data"])

market_service = MarketService()


@router.get("/prices", response_model=List[MarketDataResponse])
async def get_market_prices(
    symbols: Optional[str] = Query(None, description="Comma-separated list of symbols"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current market prices for cryptocurrencies."""
    # Try to get from cache first
    cache_key = f"market:prices:{symbols or 'all'}"
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        return cached_data

    # Fetch from service
    symbol_list = symbols.split(",") if symbols else None
    market_data = await market_service.get_market_data(symbol_list)

    # Cache for 5 seconds
    await redis_client.set(cache_key, market_data, expire=5)

    return market_data


@router.get("/candlestick/{symbol}", response_model=List[CandlestickResponse])
async def get_candlestick_data(
    symbol: str,
    interval: str = Query("1h", description="Time interval (1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of candles"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get candlestick data for a symbol."""
    # Try cache first
    cache_key = f"market:candlestick:{symbol}:{interval}:{limit}"
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        return cached_data

    # Fetch from service
    candlestick_data = await market_service.get_candlestick_data(
        symbol, interval, limit
    )

    # Cache for 30 seconds
    await redis_client.set(cache_key, candlestick_data, expire=30)

    return candlestick_data


@router.get("/indicators/{symbol}", response_model=TechnicalIndicatorsResponse)
async def get_technical_indicators(
    symbol: str,
    interval: str = Query("1h", description="Time interval"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get technical indicators for a symbol."""
    # Try cache first
    cache_key = f"market:indicators:{symbol}:{interval}"
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        return cached_data

    # Fetch from service
    indicators = await market_service.get_technical_indicators(symbol, interval)

    # Cache for 30 seconds
    await redis_client.set(cache_key, indicators, expire=30)

    return indicators
