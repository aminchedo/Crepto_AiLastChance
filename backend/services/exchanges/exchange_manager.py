import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .base_exchange import BaseExchange, ExchangeStatus
from .binance_exchange import BinanceExchange
from .coingecko_exchange import CoinGeckoExchange

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Data source priority enumeration"""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    FALLBACK = "fallback"


class ExchangeManager:
    """
    Unified exchange manager with failover and data aggregation.
    Manages multiple exchange connections with automatic failover.
    """

    def __init__(self):
        self.exchanges: Dict[str, BaseExchange] = {}
        self.primary_exchange: Optional[str] = None
        self.secondary_exchange: Optional[str] = None
        self.fallback_exchange: Optional[str] = None

        self.health_check_interval = 60  # seconds
        self.failover_enabled = True
        self.retry_attempts = 3
        self.retry_delay = 2  # seconds

        self._health_check_task: Optional[asyncio.Task] = None
        self._is_running = False

    async def add_exchange(
        self,
        name: str,
        exchange: BaseExchange,
        priority: DataSource = DataSource.FALLBACK,
    ) -> None:
        """
        Add an exchange to the manager.

        Args:
            name: Exchange identifier
            exchange: Exchange instance
            priority: Data source priority
        """
        self.exchanges[name] = exchange

        if priority == DataSource.PRIMARY:
            self.primary_exchange = name
        elif priority == DataSource.SECONDARY:
            self.secondary_exchange = name
        elif priority == DataSource.FALLBACK:
            self.fallback_exchange = name

        logger.info(f"Added exchange {name} with priority {priority.value}")

    async def connect_all(self) -> Dict[str, bool]:
        """
        Connect to all configured exchanges.

        Returns:
            Dict mapping exchange name to connection success status
        """
        results = {}

        for name, exchange in self.exchanges.items():
            try:
                success = await exchange.connect()
                results[name] = success
                logger.info(
                    f"Exchange {name} connection: {'success' if success else 'failed'}"
                )
            except Exception as e:
                logger.error(f"Failed to connect to {name}: {str(e)}")
                results[name] = False

        # Start health check monitoring
        if not self._is_running:
            self._is_running = True
            self._health_check_task = asyncio.create_task(self._health_check_loop())

        return results

    async def disconnect_all(self) -> None:
        """Disconnect from all exchanges."""
        self._is_running = False

        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        for name, exchange in self.exchanges.items():
            try:
                await exchange.disconnect()
                logger.info(f"Disconnected from {name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {name}: {str(e)}")

    async def _health_check_loop(self) -> None:
        """Periodic health check for all exchanges."""
        while self._is_running:
            try:
                await asyncio.sleep(self.health_check_interval)

                for name, exchange in self.exchanges.items():
                    try:
                        is_healthy = await exchange.health_check()

                        if (
                            not is_healthy
                            and exchange.get_status() == ExchangeStatus.CONNECTED
                        ):
                            logger.warning(
                                f"Exchange {name} health check failed, attempting reconnect"
                            )
                            await exchange.disconnect()
                            await exchange.connect()
                    except Exception as e:
                        logger.error(f"Health check error for {name}: {str(e)}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {str(e)}")

    async def _execute_with_failover(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute operation with automatic failover.

        Args:
            operation: Async function to execute
            *args, **kwargs: Arguments for the operation

        Returns:
            Result from the operation

        Raises:
            Exception if all exchanges fail
        """
        # Try exchanges in priority order
        exchange_order = [
            self.primary_exchange,
            self.secondary_exchange,
            self.fallback_exchange,
        ]

        last_error = None

        for exchange_name in exchange_order:
            if not exchange_name or exchange_name not in self.exchanges:
                continue

            exchange = self.exchanges[exchange_name]

            # Skip if exchange is not connected
            if exchange.get_status() != ExchangeStatus.CONNECTED:
                logger.warning(f"Skipping {exchange_name} - not connected")
                continue

            # Try operation with retries
            for attempt in range(self.retry_attempts):
                try:
                    result = await operation(exchange, *args, **kwargs)
                    logger.debug(
                        f"Operation succeeded on {exchange_name} (attempt {attempt + 1})"
                    )
                    return result

                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Operation failed on {exchange_name} (attempt {attempt + 1}): {str(e)}"
                    )

                    if attempt < self.retry_attempts - 1:
                        await asyncio.sleep(self.retry_delay)

        # All exchanges failed
        error_msg = f"All exchanges failed. Last error: {str(last_error)}"
        logger.error(error_msg)
        raise Exception(error_msg)

    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker with automatic failover."""

        async def _get_ticker(exchange: BaseExchange, symbol: str):
            return await exchange.get_ticker(symbol)

        return await self._execute_with_failover(_get_ticker, symbol)

    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get order book with automatic failover."""

        async def _get_orderbook(exchange: BaseExchange, symbol: str, limit: int):
            return await exchange.get_orderbook(symbol, limit)

        return await self._execute_with_failover(_get_orderbook, symbol, limit)

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """Get klines with automatic failover."""

        async def _get_klines(
            exchange: BaseExchange,
            symbol: str,
            interval: str,
            start_time: Optional[datetime],
            end_time: Optional[datetime],
            limit: int,
        ):
            return await exchange.get_klines(
                symbol, interval, start_time, end_time, limit
            )

        return await self._execute_with_failover(
            _get_klines, symbol, interval, start_time, end_time, limit
        )

    async def get_multiple_tickers(
        self, symbols: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get tickers for multiple symbols concurrently.

        Args:
            symbols: List of symbols to fetch

        Returns:
            Dict mapping symbol to ticker data
        """
        tasks = [self.get_ticker(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        tickers = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to get ticker for {symbol}: {str(result)}")
            else:
                tickers[symbol] = result

        return tickers

    async def aggregate_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Aggregate market data from multiple sources.

        Args:
            symbol: Trading pair symbol

        Returns:
            Aggregated market data with source attribution
        """
        data_sources = {}

        for name, exchange in self.exchanges.items():
            if exchange.get_status() != ExchangeStatus.CONNECTED:
                continue

            try:
                ticker = await exchange.get_ticker(symbol)
                data_sources[name] = ticker
            except Exception as e:
                logger.warning(f"Failed to get data from {name}: {str(e)}")

        if not data_sources:
            raise Exception("No data sources available")

        # Calculate aggregated metrics
        prices = [data["last_price"] for data in data_sources.values()]
        volumes = [data.get("volume_24h", 0) for data in data_sources.values()]

        return {
            "symbol": symbol,
            "aggregated_price": sum(prices) / len(prices),
            "min_price": min(prices),
            "max_price": max(prices),
            "price_spread": max(prices) - min(prices),
            "total_volume_24h": sum(volumes),
            "sources": list(data_sources.keys()),
            "source_count": len(data_sources),
            "timestamp": datetime.now(),
            "raw_data": data_sources,
        }

    def get_exchange_status(self) -> Dict[str, str]:
        """
        Get status of all exchanges.

        Returns:
            Dict mapping exchange name to status
        """
        return {
            name: exchange.get_status().value
            for name, exchange in self.exchanges.items()
        }

    def get_primary_exchange(self) -> Optional[BaseExchange]:
        """Get the primary exchange instance."""
        if self.primary_exchange and self.primary_exchange in self.exchanges:
            return self.exchanges[self.primary_exchange]
        return None

    async def subscribe_ticker_aggregated(
        self, symbol: str, callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Subscribe to ticker updates from all available sources.

        Args:
            symbol: Trading pair symbol
            callback: Function to call with aggregated ticker updates
        """

        async def exchange_callback(exchange_name: str, data: Dict[str, Any]):
            # Add source attribution
            data["source"] = exchange_name
            await callback(data)

        for name, exchange in self.exchanges.items():
            if exchange.get_status() != ExchangeStatus.CONNECTED:
                continue

            try:
                # Create partial callback with exchange name
                exchange_cb = lambda data, name=name: exchange_callback(name, data)
                await exchange.subscribe_ticker(symbol, exchange_cb)
                logger.info(f"Subscribed to {symbol} ticker on {name}")
            except NotImplementedError:
                logger.info(f"Exchange {name} does not support WebSocket subscriptions")
            except Exception as e:
                logger.error(f"Failed to subscribe to {name}: {str(e)}")

    async def unsubscribe_all(self) -> None:
        """Unsubscribe from all WebSocket streams on all exchanges."""
        for name, exchange in self.exchanges.items():
            try:
                await exchange.unsubscribe_all()
                logger.info(f"Unsubscribed from all streams on {name}")
            except Exception as e:
                logger.error(f"Error unsubscribing from {name}: {str(e)}")

    def set_failover_enabled(self, enabled: bool) -> None:
        """Enable or disable automatic failover."""
        self.failover_enabled = enabled
        logger.info(f"Failover {'enabled' if enabled else 'disabled'}")

    def set_retry_config(self, attempts: int, delay: float) -> None:
        """
        Configure retry behavior.

        Args:
            attempts: Number of retry attempts
            delay: Delay between retries in seconds
        """
        self.retry_attempts = attempts
        self.retry_delay = delay
        logger.info(f"Retry config updated: {attempts} attempts, {delay}s delay")
