import asyncio
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

from .base_exchange import BaseExchange, ExchangeStatus, OrderSide, OrderType

logger = logging.getLogger(__name__)


class BinanceExchange(BaseExchange):
    """
    Binance exchange integration with REST API and WebSocket support.
    Supports spot trading with comprehensive market data access.
    """

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        super().__init__(api_key, api_secret, testnet)

        if testnet:
            self.base_url = "https://testnet.binance.vision/api"
            self.ws_url = "wss://testnet.binance.vision/ws"
        else:
            self.base_url = "https://api.binance.com/api"
            self.ws_url = "wss://stream.binance.com:9443/ws"

        self.session: Optional[aiohttp.ClientSession] = None
        self.ws_connections: Dict[str, Any] = {}

        # Binance rate limits (requests per minute)
        self.rate_limits = {
            "ticker": 1200,
            "orderbook": 1200,
            "klines": 1200,
            "account": 1200,
            "orders": 1200,
        }

    async def connect(self) -> bool:
        """Establish connection to Binance API."""
        try:
            self.session = aiohttp.ClientSession()

            # Test connectivity
            async with self.session.get(f"{self.base_url}/v3/ping") as response:
                if response.status == 200:
                    self._set_status(ExchangeStatus.CONNECTED)
                    logger.info("Successfully connected to Binance")
                    return True
                else:
                    self._set_status(
                        ExchangeStatus.ERROR, f"Connection failed: {response.status}"
                    )
                    return False

        except Exception as e:
            self._set_status(ExchangeStatus.ERROR, str(e))
            logger.error(f"Failed to connect to Binance: {str(e)}")
            return False

    async def disconnect(self) -> None:
        """Close connection to Binance."""
        try:
            await self.unsubscribe_all()

            if self.session:
                await self.session.close()
                self.session = None

            self._set_status(ExchangeStatus.DISCONNECTED)
            logger.info("Disconnected from Binance")

        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")

    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """Generate HMAC SHA256 signature for authenticated requests."""
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        """Make HTTP request to Binance API."""
        if not self.session:
            raise RuntimeError("Not connected to exchange")

        url = f"{self.base_url}{endpoint}"
        params = params or {}

        headers = {"X-MBX-APIKEY": self.api_key}

        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params["signature"] = self._generate_signature(params)

        try:
            async with self.session.request(
                method, url, params=params, headers=headers
            ) as response:
                data = await response.json()

                if response.status != 200:
                    error_msg = data.get("msg", "Unknown error")
                    raise Exception(f"Binance API error: {error_msg}")

                return data

        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker data for a symbol."""
        symbol = self.normalize_symbol(symbol)

        data = await self._make_request("GET", "/v3/ticker/24hr", {"symbol": symbol})

        return {
            "symbol": symbol,
            "last_price": float(data["lastPrice"]),
            "bid": float(data["bidPrice"]),
            "ask": float(data["askPrice"]),
            "volume_24h": float(data["volume"]),
            "change_24h": float(data["priceChangePercent"]) / 100,
            "high_24h": float(data["highPrice"]),
            "low_24h": float(data["lowPrice"]),
            "timestamp": datetime.fromtimestamp(data["closeTime"] / 1000),
        }

    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get order book for a symbol."""
        symbol = self.normalize_symbol(symbol)

        data = await self._make_request(
            "GET", "/v3/depth", {"symbol": symbol, "limit": limit}
        )

        return {
            "bids": [(float(price), float(qty)) for price, qty in data["bids"]],
            "asks": [(float(price), float(qty)) for price, qty in data["asks"]],
            "timestamp": datetime.now(),
        }

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """Get candlestick/kline data."""
        symbol = self.normalize_symbol(symbol)

        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": min(limit, 1000),  # Binance max is 1000
        }

        if start_time:
            params["startTime"] = int(start_time.timestamp() * 1000)
        if end_time:
            params["endTime"] = int(end_time.timestamp() * 1000)

        data = await self._make_request("GET", "/v3/klines", params)

        klines = []
        for candle in data:
            klines.append(
                {
                    "timestamp": datetime.fromtimestamp(candle[0] / 1000),
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5]),
                    "close_time": datetime.fromtimestamp(candle[6] / 1000),
                    "quote_volume": float(candle[7]),
                    "trades": int(candle[8]),
                }
            )

        return klines

    async def get_account_balance(self) -> Dict[str, float]:
        """Get account balance for all assets."""
        data = await self._make_request("GET", "/v3/account", signed=True)

        balances = {}
        for balance in data["balances"]:
            free = float(balance["free"])
            locked = float(balance["locked"])
            total = free + locked

            if total > 0:
                balances[balance["asset"]] = {
                    "free": free,
                    "locked": locked,
                    "total": total,
                }

        return balances

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
        """Place a new order."""
        symbol = self.normalize_symbol(symbol)

        params = {
            "symbol": symbol,
            "side": side.value.upper(),
            "type": order_type.value.upper(),
            "quantity": quantity,
        }

        if order_type == OrderType.LIMIT:
            if price is None:
                raise ValueError("Price required for limit orders")
            params["price"] = price
            params["timeInForce"] = time_in_force

        if order_type == OrderType.STOP_LOSS and stop_price:
            params["stopPrice"] = stop_price

        data = await self._make_request("POST", "/v3/order", params, signed=True)

        return {
            "order_id": str(data["orderId"]),
            "symbol": data["symbol"],
            "side": data["side"].lower(),
            "type": data["type"].lower(),
            "quantity": float(data["origQty"]),
            "price": float(data["price"]) if data.get("price") else None,
            "status": data["status"].lower(),
            "timestamp": datetime.fromtimestamp(data["transactTime"] / 1000),
        }

    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an existing order."""
        symbol = self.normalize_symbol(symbol)

        try:
            await self._make_request(
                "DELETE",
                "/v3/order",
                {"symbol": symbol, "orderId": order_id},
                signed=True,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order: {str(e)}")
            return False

    async def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Get status of an order."""
        symbol = self.normalize_symbol(symbol)

        data = await self._make_request(
            "GET", "/v3/order", {"symbol": symbol, "orderId": order_id}, signed=True
        )

        return {
            "order_id": str(data["orderId"]),
            "symbol": data["symbol"],
            "side": data["side"].lower(),
            "type": data["type"].lower(),
            "quantity": float(data["origQty"]),
            "executed_quantity": float(data["executedQty"]),
            "price": float(data["price"]) if data.get("price") else None,
            "status": data["status"].lower(),
            "timestamp": datetime.fromtimestamp(data["time"] / 1000),
        }

    async def get_open_orders(
        self, symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all open orders."""
        params = {}
        if symbol:
            params["symbol"] = self.normalize_symbol(symbol)

        data = await self._make_request("GET", "/v3/openOrders", params, signed=True)

        orders = []
        for order in data:
            orders.append(
                {
                    "order_id": str(order["orderId"]),
                    "symbol": order["symbol"],
                    "side": order["side"].lower(),
                    "type": order["type"].lower(),
                    "quantity": float(order["origQty"]),
                    "executed_quantity": float(order["executedQty"]),
                    "price": float(order["price"]) if order.get("price") else None,
                    "status": order["status"].lower(),
                    "timestamp": datetime.fromtimestamp(order["time"] / 1000),
                }
            )

        return orders

    async def get_trade_history(
        self,
        symbol: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """Get trade history."""
        symbol = self.normalize_symbol(symbol)

        params = {"symbol": symbol, "limit": min(limit, 1000)}

        if start_time:
            params["startTime"] = int(start_time.timestamp() * 1000)
        if end_time:
            params["endTime"] = int(end_time.timestamp() * 1000)

        data = await self._make_request("GET", "/v3/myTrades", params, signed=True)

        trades = []
        for trade in data:
            trades.append(
                {
                    "trade_id": str(trade["id"]),
                    "order_id": str(trade["orderId"]),
                    "symbol": trade["symbol"],
                    "side": "buy" if trade["isBuyer"] else "sell",
                    "price": float(trade["price"]),
                    "quantity": float(trade["qty"]),
                    "commission": float(trade["commission"]),
                    "commission_asset": trade["commissionAsset"],
                    "timestamp": datetime.fromtimestamp(trade["time"] / 1000),
                }
            )

        return trades

    async def subscribe_ticker(self, symbol: str, callback) -> None:
        """Subscribe to real-time ticker updates via WebSocket."""
        symbol = self.normalize_symbol(symbol).lower()
        stream = f"{symbol}@ticker"

        await self._subscribe_ws(stream, callback, "ticker")

    async def subscribe_orderbook(self, symbol: str, callback) -> None:
        """Subscribe to real-time order book updates via WebSocket."""
        symbol = self.normalize_symbol(symbol).lower()
        stream = f"{symbol}@depth20@100ms"

        await self._subscribe_ws(stream, callback, "orderbook")

    async def subscribe_trades(self, symbol: str, callback) -> None:
        """Subscribe to real-time trade updates via WebSocket."""
        symbol = self.normalize_symbol(symbol).lower()
        stream = f"{symbol}@trade"

        await self._subscribe_ws(stream, callback, "trades")

    async def _subscribe_ws(self, stream: str, callback, stream_type: str) -> None:
        """Internal method to handle WebSocket subscriptions."""
        ws_url = f"{self.ws_url}/{stream}"

        async def ws_handler():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(ws_url) as ws:
                        self.ws_connections[stream] = ws
                        logger.info(f"WebSocket connected: {stream}")

                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                data = json.loads(msg.data)
                                await callback(
                                    self._parse_ws_message(data, stream_type)
                                )
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                logger.error(f"WebSocket error: {ws.exception()}")
                                break

            except Exception as e:
                logger.error(f"WebSocket handler error: {str(e)}")
            finally:
                if stream in self.ws_connections:
                    del self.ws_connections[stream]

        # Start WebSocket handler in background
        asyncio.create_task(ws_handler())

    def _parse_ws_message(
        self, data: Dict[str, Any], stream_type: str
    ) -> Dict[str, Any]:
        """Parse WebSocket message based on stream type."""
        if stream_type == "ticker":
            return {
                "symbol": data["s"],
                "last_price": float(data["c"]),
                "bid": float(data["b"]),
                "ask": float(data["a"]),
                "volume_24h": float(data["v"]),
                "change_24h": float(data["P"]) / 100,
                "timestamp": datetime.fromtimestamp(data["E"] / 1000),
            }
        elif stream_type == "orderbook":
            return {
                "bids": [(float(price), float(qty)) for price, qty in data["bids"]],
                "asks": [(float(price), float(qty)) for price, qty in data["asks"]],
                "timestamp": datetime.now(),
            }
        elif stream_type == "trades":
            return {
                "trade_id": str(data["t"]),
                "symbol": data["s"],
                "price": float(data["p"]),
                "quantity": float(data["q"]),
                "side": "buy" if data["m"] else "sell",
                "timestamp": datetime.fromtimestamp(data["T"] / 1000),
            }

        return data

    async def unsubscribe_all(self) -> None:
        """Unsubscribe from all WebSocket streams."""
        for stream, ws in list(self.ws_connections.items()):
            try:
                await ws.close()
                logger.info(f"WebSocket closed: {stream}")
            except Exception as e:
                logger.error(f"Error closing WebSocket {stream}: {str(e)}")

        self.ws_connections.clear()

    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol to Binance format (e.g., 'BTC/USDT' -> 'BTCUSDT')."""
        return symbol.replace("/", "").upper()

    def denormalize_symbol(self, symbol: str) -> str:
        """Convert Binance symbol to standard format (e.g., 'BTCUSDT' -> 'BTC/USDT')."""
        # Simple heuristic: assume USDT, BUSD, or BTC quote currency
        for quote in ["USDT", "BUSD", "BTC", "ETH", "BNB"]:
            if symbol.endswith(quote):
                base = symbol[: -len(quote)]
                return f"{base}/{quote}"
        return symbol
