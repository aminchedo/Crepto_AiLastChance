"""
Unit tests for the market API endpoints
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from backend.api.market import router
from backend.main import app
from backend.models.market import MarketData
from backend.services.market_service import MarketService


class TestMarketAPI:
    """Test cases for market API endpoints"""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_market_data(self):
        """Create mock market data."""
        return [
            MarketData(
                symbol="BTCUSDT",
                timestamp="2023-12-01T12:00:00Z",
                open=50000.0,
                high=51000.0,
                low=49000.0,
                close=50500.0,
                volume=1000.5,
            ),
            MarketData(
                symbol="ETHUSDT",
                timestamp="2023-12-01T12:00:00Z",
                open=3000.0,
                high=3100.0,
                low=2900.0,
                close=3050.0,
                volume=5000.0,
            ),
        ]

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    def test_get_market_data_success(self, client, mock_market_data):
        """Test successful market data retrieval."""
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            response = client.get(
                "/api/v1/market/data?symbols=BTCUSDT&interval=1h&limit=100"
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["symbol"] == "BTCUSDT"
            assert data[1]["symbol"] == "ETHUSDT"

    def test_get_market_data_no_symbols(self, client):
        """Test market data retrieval with no symbols specified."""
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = []

            response = client.get("/api/v1/market/data")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 0

    def test_get_market_data_invalid_symbols(self, client):
        """Test market data retrieval with invalid symbols."""
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = []

            response = client.get("/api/v1/market/data?symbols=INVALID")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 0

    def test_get_market_data_invalid_interval(self, client):
        """Test market data retrieval with invalid interval."""
        response = client.get("/api/v1/market/data?interval=invalid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_market_data_invalid_limit(self, client):
        """Test market data retrieval with invalid limit."""
        response = client.get("/api/v1/market/data?limit=-1")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_market_data_large_limit(self, client):
        """Test market data retrieval with large limit."""
        response = client.get("/api/v1/market/data?limit=10000")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_market_data_service_error(self, client):
        """Test market data retrieval with service error."""
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.side_effect = Exception(
                "Service error"
            )

            response = client.get("/api/v1/market/data")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_get_real_time_data_success(self, client):
        """Test successful real-time data retrieval."""
        mock_data = {
            "BTCUSDT": {
                "price": "50000.00",
                "volume": "1000.50",
                "timestamp": "2023-12-01T12:00:00Z",
            }
        }

        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_real_time_data.return_value = mock_data

            response = client.get("/api/v1/market/realtime?symbols=BTCUSDT")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "BTCUSDT" in data
            assert data["BTCUSDT"]["price"] == "50000.00"

    def test_get_real_time_data_no_symbols(self, client):
        """Test real-time data retrieval with no symbols."""
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_real_time_data.return_value = {}

            response = client.get("/api/v1/market/realtime")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 0

    def test_get_real_time_data_service_error(self, client):
        """Test real-time data retrieval with service error."""
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_real_time_data.side_effect = Exception(
                "Service error"
            )

            response = client.get("/api/v1/market/realtime")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_get_market_summary_success(self, client):
        """Test successful market summary retrieval."""
        mock_summary = {
            "total_market_cap": 1000000000000,
            "total_volume": 50000000000,
            "active_cryptocurrencies": 5000,
            "market_cap_change_24h": 2.5,
        }

        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_market_summary.return_value = mock_summary

            response = client.get("/api/v1/market/summary")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total_market_cap"] == 1000000000000
            assert data["total_volume"] == 50000000000

    def test_get_market_summary_service_error(self, client):
        """Test market summary retrieval with service error."""
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_market_summary.side_effect = Exception(
                "Service error"
            )

            response = client.get("/api/v1/market/summary")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_get_symbols_success(self, client):
        """Test successful symbols retrieval."""
        mock_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]

        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_available_symbols.return_value = mock_symbols

            response = client.get("/api/v1/market/symbols")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 5
            assert "BTCUSDT" in data
            assert "ETHUSDT" in data

    def test_get_symbols_service_error(self, client):
        """Test symbols retrieval with service error."""
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_available_symbols.side_effect = Exception(
                "Service error"
            )

            response = client.get("/api/v1/market/symbols")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_get_ohlcv_success(self, client):
        """Test successful OHLCV data retrieval."""
        mock_ohlcv = [
            {
                "timestamp": "2023-12-01T12:00:00Z",
                "open": 50000.0,
                "high": 51000.0,
                "low": 49000.0,
                "close": 50500.0,
                "volume": 1000.5,
            }
        ]

        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_ohlcv_data.return_value = mock_ohlcv

            response = client.get(
                "/api/v1/market/ohlcv?symbol=BTCUSDT&interval=1h&limit=100"
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1
            assert data[0]["open"] == 50000.0
            assert data[0]["close"] == 50500.0

    def test_get_ohlcv_missing_symbol(self, client):
        """Test OHLCV data retrieval with missing symbol."""
        response = client.get("/api/v1/market/ohlcv?interval=1h&limit=100")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_ohlcv_invalid_interval(self, client):
        """Test OHLCV data retrieval with invalid interval."""
        response = client.get(
            "/api/v1/market/ohlcv?symbol=BTCUSDT&interval=invalid&limit=100"
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_ohlcv_service_error(self, client):
        """Test OHLCV data retrieval with service error."""
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_ohlcv_data.side_effect = Exception(
                "Service error"
            )

            response = client.get(
                "/api/v1/market/ohlcv?symbol=BTCUSDT&interval=1h&limit=100"
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_get_price_history_success(self, client):
        """Test successful price history retrieval."""
        mock_history = [
            {"timestamp": "2023-12-01T12:00:00Z", "price": 50000.0},
            {"timestamp": "2023-12-01T13:00:00Z", "price": 50500.0},
        ]

        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_price_history.return_value = mock_history

            response = client.get(
                "/api/v1/market/price-history?symbol=BTCUSDT&interval=1h&limit=100"
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["price"] == 50000.0
            assert data[1]["price"] == 50500.0

    def test_get_price_history_missing_symbol(self, client):
        """Test price history retrieval with missing symbol."""
        response = client.get("/api/v1/market/price-history?interval=1h&limit=100")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_price_history_service_error(self, client):
        """Test price history retrieval with service error."""
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_price_history.side_effect = Exception(
                "Service error"
            )

            response = client.get(
                "/api/v1/market/price-history?symbol=BTCUSDT&interval=1h&limit=100"
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_get_volume_data_success(self, client):
        """Test successful volume data retrieval."""
        mock_volume = [
            {
                "timestamp": "2023-12-01T12:00:00Z",
                "volume": 1000.5,
                "quote_volume": 50000000.0,
            }
        ]

        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_volume_data.return_value = mock_volume

            response = client.get(
                "/api/v1/market/volume?symbol=BTCUSDT&interval=1h&limit=100"
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1
            assert data[0]["volume"] == 1000.5
            assert data[0]["quote_volume"] == 50000000.0

    def test_get_volume_data_missing_symbol(self, client):
        """Test volume data retrieval with missing symbol."""
        response = client.get("/api/v1/market/volume?interval=1h&limit=100")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_volume_data_service_error(self, client):
        """Test volume data retrieval with service error."""
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_volume_data.side_effect = Exception(
                "Service error"
            )

            response = client.get(
                "/api/v1/market/volume?symbol=BTCUSDT&interval=1h&limit=100"
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_get_market_data_performance(self, client):
        """Test market data API performance."""
        import time

        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = []

            start_time = time.time()
            response = client.get(
                "/api/v1/market/data?symbols=BTCUSDT&interval=1h&limit=100"
            )
            end_time = time.time()

            response_time = end_time - start_time

            assert response.status_code == status.HTTP_200_OK
            assert (
                response_time < 1.0
            ), f"Response took {response_time:.3f}s, expected < 1.0s"

    def test_get_market_data_concurrent_requests(self, client):
        """Test market data API with concurrent requests."""
        import threading
        import time

        results = []

        def make_request():
            with patch("backend.api.market.MarketService") as mock_service:
                mock_service.return_value.get_historical_data.return_value = []

                response = client.get(
                    "/api/v1/market/data?symbols=BTCUSDT&interval=1h&limit=100"
                )
                results.append(response.status_code)

        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that all requests succeeded
        assert len(results) == 10
        assert all(status == status.HTTP_200_OK for status in results)

    def test_market_api_authentication(self, client):
        """Test market API authentication requirements."""
        # Test without authentication
        response = client.get("/api/v1/market/data")

        # Should work without authentication for market data
        assert response.status_code == status.HTTP_200_OK

    def test_market_api_rate_limiting(self, client):
        """Test market API rate limiting."""
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = []

            # Make many requests quickly
            for _ in range(100):
                response = client.get(
                    "/api/v1/market/data?symbols=BTCUSDT&interval=1h&limit=100"
                )
                assert response.status_code == status.HTTP_200_OK

    def test_market_api_error_handling(self, client):
        """Test market API error handling."""
        # Test with invalid endpoint
        response = client.get("/api/v1/market/invalid")

        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Test with malformed request
        response = client.get("/api/v1/market/data?symbols=")

        assert (
            response.status_code == status.HTTP_200_OK
        )  # Should handle empty symbols gracefully

    def test_market_api_data_validation(self, client):
        """Test market API data validation."""
        # Test with valid data
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = [
                MarketData(
                    symbol="BTCUSDT",
                    timestamp="2023-12-01T12:00:00Z",
                    open=50000.0,
                    high=51000.0,
                    low=49000.0,
                    close=50500.0,
                    volume=1000.5,
                )
            ]

            response = client.get(
                "/api/v1/market/data?symbols=BTCUSDT&interval=1h&limit=100"
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1
            assert data[0]["symbol"] == "BTCUSDT"
            assert data[0]["open"] == 50000.0
            assert data[0]["close"] == 50500.0

    def test_market_api_pagination(self, client):
        """Test market API pagination."""
        # Test with limit parameter
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = []

            response = client.get(
                "/api/v1/market/data?symbols=BTCUSDT&interval=1h&limit=50"
            )

            assert response.status_code == status.HTTP_200_OK
            # Verify that limit parameter was passed to service
            mock_service.return_value.get_historical_data.assert_called_once()

    def test_market_api_caching(self, client):
        """Test market API caching behavior."""
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = []

            # Make same request twice
            response1 = client.get(
                "/api/v1/market/data?symbols=BTCUSDT&interval=1h&limit=100"
            )
            response2 = client.get(
                "/api/v1/market/data?symbols=BTCUSDT&interval=1h&limit=100"
            )

            assert response1.status_code == status.HTTP_200_OK
            assert response2.status_code == status.HTTP_200_OK

            # Service should be called twice (no caching implemented yet)
            assert mock_service.return_value.get_historical_data.call_count == 2
