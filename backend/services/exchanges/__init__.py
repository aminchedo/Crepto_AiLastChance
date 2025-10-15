"""
Exchange integration module for cryptocurrency market data and trading.

Provides unified interface for multiple exchanges with automatic failover,
rate limiting, and comprehensive error handling.

Supported Exchanges:
- Binance: Full REST API and WebSocket support for spot trading
- CoinGecko: Market data aggregation and historical price data

Features:
- Automatic failover between exchanges
- Rate limit management
- Health monitoring and automatic reconnection
- Data aggregation from multiple sources
- WebSocket real-time data streaming
- Unified symbol normalization
"""

from .base_exchange import BaseExchange, ExchangeStatus, OrderSide, OrderType
from .binance_exchange import BinanceExchange
from .coingecko_exchange import CoinGeckoExchange
from .exchange_manager import DataSource, ExchangeManager

__all__ = [
    "BaseExchange",
    "ExchangeStatus",
    "OrderSide",
    "OrderType",
    "BinanceExchange",
    "CoinGeckoExchange",
    "ExchangeManager",
    "DataSource",
]
