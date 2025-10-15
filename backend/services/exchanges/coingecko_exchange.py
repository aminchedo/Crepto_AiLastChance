import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp

from .base_exchange import BaseExchange, ExchangeStatus

logger = logging.getLogger(__name__)


class CoinGeckoExchange(BaseExchange):
    """
    CoinGecko API integration for cryptocurrency market data.
    Provides comprehensive market data, prices, and historical information.
    Note: CoinGecko does not support trading operations.
    """

    def __init__(self, api_key: Optional[str] = None, testnet: bool = False):
        super().__init__(api_key or "", "", testnet)

        self.base_url = "https://api.coingecko.com/api/v3"
        self.pro_api_url = "https://pro-api.coingecko.com/api/v3"

        # Use Pro API if key provided
        if api_key:
            self.api_url = self.pro_api_url
            self.is_pro = True
        else:
            self.api_url = self.base_url
            self.is_pro = False

        self.session: Optional[aiohttp.ClientSession] = None

        # CoinGecko rate limits (requests per minute)
        # Free tier: 10-50 calls/minute, Pro: 500 calls/minute
        self.rate_limits = {
            "ticker": 50 if self.is_pro else 10,
            "markets": 50 if self.is_pro else 10,
            "historical": 50 if self.is_pro else 10,
        }

        # Symbol mapping: standard format to CoinGecko IDs
        self.symbol_map = {
            "BTCUSDT": "bitcoin",
            "ETHUSDT": "ethereum",
            "BNBUSDT": "binancecoin",
            "ADAUSDT": "cardano",
            "SOLUSDT": "solana",
            "MATICUSDT": "matic-network",
            "DOTUSDT": "polkadot",
            "LINKUSDT": "chainlink",
            "LTCUSDT": "litecoin",
            "XRPUSDT": "ripple",
            "AVAXUSDT": "avalanche-2",
            "ATOMUSDT": "cosmos",
            "UNIUSDT": "uniswap",
            "ALGOUSDT": "algorand",
            "VETUSDT": "vechain",
        }

    async def connect(self) -> bool:
        """Establish connection to CoinGecko API."""
        try:
            self.session = aiohttp.ClientSession()

            # Test connectivity with ping
            async with self.session.get(f"{self.api_url}/ping") as response:
                if response.status == 200:
                    self._set_status(ExchangeStatus.CONNECTED)
                    logger.info(
                        f"Successfully connected to CoinGecko {'Pro' if self.is_pro else 'Free'} API"
                    )
                    return True
                else:
                    self._set_status(
                        ExchangeStatus.ERROR, f"Connection failed: {response.status}"
                    )
                    return False

        except Exception as e:
            self._set_status(ExchangeStatus.ERROR, str(e))
            logger.error(f"Failed to connect to CoinGecko: {str(e)}")
            return False

    async def disconnect(self) -> None:
        """Close connection to CoinGecko."""
        try:
            if self.session:
                await self.session.close()
                self.session = None

            self._set_status(ExchangeStatus.DISCONNECTED)
            logger.info("Disconnected from CoinGecko")

        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")

    async def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to CoinGecko API."""
        if not self.session:
            raise RuntimeError("Not connected to exchange")

        url = f"{self.api_url}{endpoint}"
        params = params or {}

        headers = {}
        if self.is_pro and self.api_key:
            headers["x-cg-pro-api-key"] = self.api_key

        try:
            async with self.session.get(
                url, params=params, headers=headers
            ) as response:
                if response.status == 429:
                    # Rate limit exceeded
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limit exceeded, retry after {retry_after}s")
                    await asyncio.sleep(retry_after)
                    return await self._make_request(endpoint, params)

                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(
                        f"CoinGecko API error {response.status}: {error_text}"
                    )

                return await response.json()

        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    def _get_coin_id(self, symbol: str) -> str:
        """Convert symbol to CoinGecko coin ID."""
        normalized = self.normalize_symbol(symbol)
        coin_id = self.symbol_map.get(normalized)

        if not coin_id:
            # Try to extract base currency
            base = (
                normalized.replace("USDT", "")
                .replace("BUSD", "")
                .replace("USD", "")
                .lower()
            )
            coin_id = base

        return coin_id

    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker data for a symbol."""
        coin_id = self._get_coin_id(symbol)

        data = await self._make_request(
            "/simple/price",
            {
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true",
                "include_last_updated_at": "true",
            },
        )

        if coin_id not in data:
            raise ValueError(f"Coin {coin_id} not found in CoinGecko")

        coin_data = data[coin_id]

        return {
            "symbol": symbol,
            "last_price": float(coin_data["usd"]),
            "bid": float(coin_data["usd"]) * 0.999,  # Approximate bid
            "ask": float(coin_data["usd"]) * 1.001,  # Approximate ask
            "volume_24h": float(coin_data.get("usd_24h_vol", 0)),
            "change_24h": float(coin_data.get("usd_24h_change", 0)) / 100,
            "market_cap": float(coin_data.get("usd_market_cap", 0)),
            "timestamp": datetime.fromtimestamp(coin_data.get("last_updated_at", 0)),
        }

    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """CoinGecko does not provide order book data."""
        raise NotImplementedError("CoinGecko does not support order book data")

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """Get historical price data (OHLC)."""
        coin_id = self._get_coin_id(symbol)

        # CoinGecko uses days parameter for historical data
        if not start_time:
            start_time = datetime.now() - timedelta(days=365)

        days = (datetime.now() - start_time).days
        days = min(days, 365)  # CoinGecko free tier limit

        data = await self._make_request(
            f"/coins/{coin_id}/ohlc", {"vs_currency": "usd", "days": days}
        )

        klines = []
        for candle in data:
            # CoinGecko OHLC format: [timestamp, open, high, low, close]
            klines.append(
                {
                    "timestamp": datetime.fromtimestamp(candle[0] / 1000),
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": 0.0,  # CoinGecko OHLC doesn't include volume
                }
            )

        # Apply limit
        if limit and len(klines) > limit:
            klines = klines[-limit:]

        return klines

    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive market data for a coin."""
        coin_id = self._get_coin_id(symbol)

        data = await self._make_request(
            f"/coins/{coin_id}",
            {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false",
                "sparkline": "false",
            },
        )

        market_data = data.get("market_data", {})

        return {
            "symbol": symbol,
            "name": data.get("name"),
            "current_price": float(market_data.get("current_price", {}).get("usd", 0)),
            "market_cap": float(market_data.get("market_cap", {}).get("usd", 0)),
            "market_cap_rank": market_data.get("market_cap_rank"),
            "total_volume": float(market_data.get("total_volume", {}).get("usd", 0)),
            "high_24h": float(market_data.get("high_24h", {}).get("usd", 0)),
            "low_24h": float(market_data.get("low_24h", {}).get("usd", 0)),
            "price_change_24h": float(market_data.get("price_change_24h", 0)),
            "price_change_percentage_24h": float(
                market_data.get("price_change_percentage_24h", 0)
            ),
            "price_change_percentage_7d": float(
                market_data.get("price_change_percentage_7d", 0)
            ),
            "price_change_percentage_30d": float(
                market_data.get("price_change_percentage_30d", 0)
            ),
            "circulating_supply": float(market_data.get("circulating_supply", 0)),
            "total_supply": float(market_data.get("total_supply", 0)),
            "max_supply": (
                float(market_data.get("max_supply", 0))
                if market_data.get("max_supply")
                else None
            ),
            "ath": float(market_data.get("ath", {}).get("usd", 0)),
            "ath_change_percentage": float(
                market_data.get("ath_change_percentage", {}).get("usd", 0)
            ),
            "ath_date": market_data.get("ath_date", {}).get("usd"),
            "atl": float(market_data.get("atl", {}).get("usd", 0)),
            "atl_change_percentage": float(
                market_data.get("atl_change_percentage", {}).get("usd", 0)
            ),
            "atl_date": market_data.get("atl_date", {}).get("usd"),
            "last_updated": data.get("last_updated"),
        }

    async def get_trending_coins(self) -> List[Dict[str, Any]]:
        """Get trending coins on CoinGecko."""
        data = await self._make_request("/search/trending")

        trending = []
        for item in data.get("coins", []):
            coin = item.get("item", {})
            trending.append(
                {
                    "coin_id": coin.get("id"),
                    "name": coin.get("name"),
                    "symbol": coin.get("symbol"),
                    "market_cap_rank": coin.get("market_cap_rank"),
                    "thumb": coin.get("thumb"),
                    "price_btc": float(coin.get("price_btc", 0)),
                }
            )

        return trending

    async def get_global_data(self) -> Dict[str, Any]:
        """Get global cryptocurrency market data."""
        data = await self._make_request("/global")

        global_data = data.get("data", {})

        return {
            "active_cryptocurrencies": global_data.get("active_cryptocurrencies"),
            "markets": global_data.get("markets"),
            "total_market_cap": global_data.get("total_market_cap", {}).get("usd", 0),
            "total_volume": global_data.get("total_volume", {}).get("usd", 0),
            "market_cap_percentage": global_data.get("market_cap_percentage", {}),
            "market_cap_change_percentage_24h": global_data.get(
                "market_cap_change_percentage_24h_usd", 0
            ),
            "updated_at": global_data.get("updated_at"),
        }

    # Trading operations not supported by CoinGecko
    async def get_account_balance(self) -> Dict[str, float]:
        """CoinGecko does not support trading operations."""
        raise NotImplementedError("CoinGecko does not support trading operations")

    async def place_order(self, *args, **kwargs) -> Dict[str, Any]:
        """CoinGecko does not support trading operations."""
        raise NotImplementedError("CoinGecko does not support trading operations")

    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """CoinGecko does not support trading operations."""
        raise NotImplementedError("CoinGecko does not support trading operations")

    async def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """CoinGecko does not support trading operations."""
        raise NotImplementedError("CoinGecko does not support trading operations")

    async def get_open_orders(
        self, symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """CoinGecko does not support trading operations."""
        raise NotImplementedError("CoinGecko does not support trading operations")

    async def get_trade_history(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """CoinGecko does not support trading operations."""
        raise NotImplementedError("CoinGecko does not support trading operations")

    # WebSocket operations not supported by CoinGecko
    async def subscribe_ticker(self, symbol: str, callback) -> None:
        """CoinGecko does not support WebSocket subscriptions."""
        raise NotImplementedError("CoinGecko does not support WebSocket subscriptions")

    async def subscribe_orderbook(self, symbol: str, callback) -> None:
        """CoinGecko does not support WebSocket subscriptions."""
        raise NotImplementedError("CoinGecko does not support WebSocket subscriptions")

    async def subscribe_trades(self, symbol: str, callback) -> None:
        """CoinGecko does not support WebSocket subscriptions."""
        raise NotImplementedError("CoinGecko does not support WebSocket subscriptions")

    async def unsubscribe_all(self) -> None:
        """No WebSocket connections to close."""
        pass

    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol to standard format."""
        return symbol.replace("/", "").upper()

    def denormalize_symbol(self, symbol: str) -> str:
        """Convert to standard format."""
        # CoinGecko uses coin IDs, not trading pairs
        return symbol
