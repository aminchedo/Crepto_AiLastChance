import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ExchangeStatus(Enum):
    """Exchange connection status"""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


class OrderSide(Enum):
    """Order side enumeration"""

    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order type enumeration"""

    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class BaseExchange(ABC):
    """
    Abstract base class for cryptocurrency exchange integrations.
    Provides unified interface for market data, trading, and account management.
    """

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.status = ExchangeStatus.DISCONNECTED
        self.last_error: Optional[str] = None
        self.rate_limits: Dict[str, int] = {}
        self.request_counts: Dict[str, int] = {}

    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the exchange.
        Returns True if successful, False otherwise.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the exchange."""
        pass

    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Get current ticker data for a symbol.

        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')

        Returns:
            Dict containing:
                - symbol: str
                - last_price: float
                - bid: float
                - ask: float
                - volume_24h: float
                - change_24h: float
                - timestamp: datetime
        """
        pass

    @abstractmethod
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get order book for a symbol.

        Args:
            symbol: Trading pair symbol
            limit: Number of levels to retrieve

        Returns:
            Dict containing:
                - bids: List[Tuple[float, float]] (price, quantity)
                - asks: List[Tuple[float, float]] (price, quantity)
                - timestamp: datetime
        """
        pass

    @abstractmethod
    async def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """
        Get candlestick/kline data.

        Args:
            symbol: Trading pair symbol
            interval: Timeframe (e.g., '1m', '5m', '1h', '1d')
            start_time: Start time for historical data
            end_time: End time for historical data
            limit: Maximum number of candles

        Returns:
            List of dicts containing:
                - timestamp: datetime
                - open: float
                - high: float
                - low: float
                - close: float
                - volume: float
        """
        pass

    @abstractmethod
    async def get_account_balance(self) -> Dict[str, float]:
        """
        Get account balance for all assets.

        Returns:
            Dict mapping asset symbol to available balance
        """
        pass

    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "GTC",
    ) -> Dict[str, Any]:
        """
        Place a new order.

        Args:
            symbol: Trading pair symbol
            side: Buy or sell
            order_type: Market, limit, stop loss, etc.
            quantity: Order quantity
            price: Limit price (required for limit orders)
            stop_price: Stop price (required for stop orders)
            time_in_force: Time in force (GTC, IOC, FOK)

        Returns:
            Dict containing:
                - order_id: str
                - symbol: str
                - side: str
                - type: str
                - quantity: float
                - price: float
                - status: str
                - timestamp: datetime
        """
        pass

    @abstractmethod
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """
        Cancel an existing order.

        Args:
            symbol: Trading pair symbol
            order_id: Order ID to cancel

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """
        Get status of an order.

        Args:
            symbol: Trading pair symbol
            order_id: Order ID

        Returns:
            Dict containing order details and current status
        """
        pass

    @abstractmethod
    async def get_open_orders(
        self, symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all open orders.

        Args:
            symbol: Optional symbol filter

        Returns:
            List of open orders
        """
        pass

    @abstractmethod
    async def get_trade_history(
        self,
        symbol: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """
        Get trade history.

        Args:
            symbol: Trading pair symbol
            start_time: Start time for history
            end_time: End time for history
            limit: Maximum number of trades

        Returns:
            List of executed trades
        """
        pass

    def get_status(self) -> ExchangeStatus:
        """Get current connection status."""
        return self.status

    def get_last_error(self) -> Optional[str]:
        """Get last error message."""
        return self.last_error

    def _set_status(self, status: ExchangeStatus, error: Optional[str] = None) -> None:
        """Update connection status and error message."""
        self.status = status
        self.last_error = error
        logger.info(f"Exchange status changed to {status.value}")
        if error:
            logger.error(f"Exchange error: {error}")

    async def health_check(self) -> bool:
        """
        Perform health check on exchange connection.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try to fetch a ticker as a basic health check
            await self.get_ticker("BTCUSDT")
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    def _check_rate_limit(self, endpoint: str) -> bool:
        """
        Check if rate limit allows request.

        Args:
            endpoint: API endpoint name

        Returns:
            True if request is allowed, False if rate limited
        """
        if endpoint not in self.rate_limits:
            return True

        current_count = self.request_counts.get(endpoint, 0)
        limit = self.rate_limits[endpoint]

        if current_count >= limit:
            logger.warning(f"Rate limit reached for endpoint: {endpoint}")
            return False

        return True

    def _increment_request_count(self, endpoint: str) -> None:
        """Increment request counter for rate limiting."""
        self.request_counts[endpoint] = self.request_counts.get(endpoint, 0) + 1

    def _reset_request_counts(self) -> None:
        """Reset all request counters (called periodically)."""
        self.request_counts.clear()

    def normalize_symbol(self, symbol: str) -> str:
        """
        Normalize symbol to exchange format.

        Args:
            symbol: Symbol in standard format (e.g., 'BTC/USDT')

        Returns:
            Symbol in exchange-specific format
        """
        # Default implementation removes slash
        return symbol.replace("/", "")

    def denormalize_symbol(self, symbol: str) -> str:
        """
        Convert exchange symbol to standard format.

        Args:
            symbol: Symbol in exchange format

        Returns:
            Symbol in standard format (e.g., 'BTC/USDT')
        """
        # Default implementation - override in subclasses
        return symbol

    @abstractmethod
    async def subscribe_ticker(self, symbol: str, callback) -> None:
        """
        Subscribe to real-time ticker updates via WebSocket.

        Args:
            symbol: Trading pair symbol
            callback: Async function to call with ticker updates
        """
        pass

    @abstractmethod
    async def subscribe_orderbook(self, symbol: str, callback) -> None:
        """
        Subscribe to real-time order book updates via WebSocket.

        Args:
            symbol: Trading pair symbol
            callback: Async function to call with order book updates
        """
        pass

    @abstractmethod
    async def subscribe_trades(self, symbol: str, callback) -> None:
        """
        Subscribe to real-time trade updates via WebSocket.

        Args:
            symbol: Trading pair symbol
            callback: Async function to call with trade updates
        """
        pass

    @abstractmethod
    async def unsubscribe_all(self) -> None:
        """Unsubscribe from all WebSocket streams."""
        pass
