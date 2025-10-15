from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SignalResponse(BaseModel):
    symbol: str
    timestamp: datetime
    signal_type: str  # BUY, SELL, HOLD
    confidence: float
    price: float
    score: float
    reasoning: str
    trend_confirmation: Optional[Dict[str, Any]] = None
    final_score: Optional[float] = None


class SignalSummaryResponse(BaseModel):
    symbol: str
    timeframes: Dict[str, Dict[str, Any]]
    overall_signal: str
    overall_score: float
    overall_confidence: float


class BacktestRequest(BaseModel):
    symbol: str
    strategy: str
    start_date: datetime
    end_date: datetime
    initial_capital: float = 10000.0
    timeframe: str = "1h"


class TradeResponse(BaseModel):
    timestamp: datetime
    action: str
    entry_price: float
    exit_price: float
    position_size: float
    gross_return: float
    net_return: float
    commission: float
    slippage: float
    capital_before: float
    capital_after: float
    pnl: float


class BacktestResponse(BaseModel):
    symbol: str
    strategy: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    avg_trade_return: float
    volatility: float
    trades: List[TradeResponse]
