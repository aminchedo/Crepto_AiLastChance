from typing import Optional

from pydantic import BaseModel


class MarketDataResponse(BaseModel):
    id: str
    symbol: str
    name: str
    price: float
    change_24h: float
    change_percent_24h: float
    volume_24h: float
    market_cap: float
    high_24h: float
    low_24h: float
    timestamp: int


class CandlestickResponse(BaseModel):
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class MACDData(BaseModel):
    macd: float
    signal: float
    histogram: float


class BollingerBands(BaseModel):
    upper: float
    middle: float
    lower: float


class TechnicalIndicatorsResponse(BaseModel):
    rsi: float
    macd: MACDData
    sma_20: float
    sma_50: float
    ema_12: float
    ema_26: float
    bb: BollingerBands
