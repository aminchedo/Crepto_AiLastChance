"""
Test configuration and fixtures for BOLT AI Neural Agent System
"""

import asyncio
import os
import sqlite3
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock

import numpy as np
import pandas as pd
import pytest
import tensorflow as tf
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.config import Settings
from backend.db.database import Base, get_db
from backend.db.sqlite_manager import SQLiteManager
from backend.models.alert import Alert
from backend.models.audit_log import AuditLog
from backend.models.model_metrics import ModelMetrics
from backend.models.portfolio import Portfolio
from backend.models.user import User


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Test settings with temporary database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    settings = Settings(
        DATABASE_URL=f"sqlite:///{db_path}",
        SQLITE_DB_PATH=db_path,
        SQLITE_ENCRYPTION_KEY="test_key_32_chars_long_12345",
        REDIS_URL="redis://localhost:6379/1",
        SECRET_KEY="test_secret_key",
        ENVIRONMENT="test",
    )

    yield settings

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def test_db(test_settings):
    """Create test database."""
    engine = create_engine(test_settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    engine.dispose()


@pytest.fixture
async def async_test_db(test_settings):
    """Create async test database."""
    engine = create_async_engine(
        test_settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def sqlite_manager(test_settings):
    """Create SQLite manager for testing."""
    manager = SQLiteManager(
        test_settings.SQLITE_DB_PATH, test_settings.SQLITE_ENCRYPTION_KEY
    )
    manager.initialize_database()
    return manager


@pytest.fixture
def mock_market_data():
    """Generate mock market data for testing."""
    dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="1H")
    np.random.seed(42)

    # Generate realistic price data
    base_price = 50000
    returns = np.random.normal(0, 0.02, len(dates))
    prices = [base_price]

    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))

    data = pd.DataFrame(
        {
            "timestamp": dates,
            "symbol": "BTCUSDT",
            "open": prices,
            "high": [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            "low": [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            "close": prices,
            "volume": np.random.uniform(1000, 10000, len(dates)),
        }
    )

    return data


@pytest.fixture
def mock_user_data():
    """Mock user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": "hashed_password_here",
        "is_active": True,
        "is_verified": True,
    }


@pytest.fixture
def mock_portfolio_data():
    """Mock portfolio data for testing."""
    return {
        "user_id": 1,
        "name": "Test Portfolio",
        "balance": 10000.0,
        "risk_tolerance": "medium",
        "strategy": "neural_ai",
    }


@pytest.fixture
def mock_alert_data():
    """Mock alert data for testing."""
    return {
        "user_id": 1,
        "symbol": "BTCUSDT",
        "alert_type": "price_above",
        "threshold": 50000.0,
        "is_active": True,
        "message": "BTC price above $50,000",
    }


@pytest.fixture
def mock_model_metrics():
    """Mock model metrics for testing."""
    return {
        "model_version": "1.0.0",
        "epoch": 100,
        "train_loss": 0.05,
        "val_loss": 0.06,
        "train_r2": 0.85,
        "val_r2": 0.82,
        "directional_accuracy": 0.75,
        "precision": 0.80,
        "recall": 0.78,
        "f1_score": 0.79,
        "sharpe_ratio": 1.5,
        "max_drawdown": 0.15,
    }


@pytest.fixture
def mock_tensorflow_model():
    """Create a mock TensorFlow model for testing."""
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Dense(64, activation="relu", input_shape=(10,)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation="relu"),
            tf.keras.layers.Dense(3, activation="softmax"),  # Bull/Bear/Neutral
        ]
    )

    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )

    return model


@pytest.fixture
def mock_prediction_data():
    """Mock prediction data for testing."""
    return {
        "symbol": "BTCUSDT",
        "timestamp": "2023-12-01T12:00:00Z",
        "bullish_probability": 0.65,
        "bearish_probability": 0.25,
        "neutral_probability": 0.10,
        "confidence": 0.75,
        "prediction": "BULL",
        "uncertainty": 0.15,
    }


@pytest.fixture
def mock_exchange_data():
    """Mock exchange API responses."""
    return {
        "binance": {
            "symbol": "BTCUSDT",
            "price": "50000.00",
            "volume": "1000.50",
            "timestamp": 1701432000000,
        },
        "coingecko": {
            "bitcoin": {
                "usd": 50000.0,
                "usd_24h_change": 2.5,
                "last_updated_at": 1701432000,
            }
        },
    }


@pytest.fixture
def mock_notification_data():
    """Mock notification data for testing."""
    return {
        "title": "Price Alert",
        "message": "BTC price above $50,000",
        "priority": "high",
        "channels": ["toast", "email"],
        "user_id": 1,
    }


@pytest.fixture
def performance_benchmarks():
    """Performance benchmark thresholds."""
    return {
        "startup_time": 5.0,  # seconds
        "prediction_latency": 0.1,  # seconds
        "ui_frame_time": 16.67,  # milliseconds (60 FPS)
        "memory_usage": 2.0,  # GB
        "directional_accuracy": 0.70,  # 70%
        "test_coverage": 0.90,  # 90%
    }


@pytest.fixture
def mock_api_responses():
    """Mock API responses for testing."""
    return {
        "market_data": {
            "status": "success",
            "data": [
                {
                    "symbol": "BTCUSDT",
                    "price": "50000.00",
                    "volume": "1000.50",
                    "timestamp": "2023-12-01T12:00:00Z",
                }
            ],
        },
        "prediction": {
            "status": "success",
            "data": {
                "symbol": "BTCUSDT",
                "prediction": "BULL",
                "confidence": 0.75,
                "probabilities": {"bullish": 0.65, "bearish": 0.25, "neutral": 0.10},
            },
        },
        "training_status": {
            "status": "success",
            "data": {
                "is_training": True,
                "current_epoch": 50,
                "max_epochs": 100,
                "metrics": {"train_loss": 0.05, "val_loss": 0.06, "accuracy": 0.85},
            },
        },
    }


@pytest.fixture
def mock_websocket_data():
    """Mock WebSocket data for testing."""
    return {
        "type": "price_update",
        "data": {
            "symbol": "BTCUSDT",
            "price": "50000.00",
            "volume": "1000.50",
            "timestamp": "2023-12-01T12:00:00Z",
        },
    }


@pytest.fixture
def mock_error_responses():
    """Mock error responses for testing."""
    return {
        "api_error": {
            "status": "error",
            "message": "API rate limit exceeded",
            "code": 429,
        },
        "network_error": {
            "status": "error",
            "message": "Network connection failed",
            "code": 500,
        },
        "validation_error": {
            "status": "error",
            "message": "Invalid input parameters",
            "code": 400,
        },
    }


@pytest.fixture
def mock_security_data():
    """Mock security-related data for testing."""
    return {
        "encryption_key": "test_encryption_key_32_chars",
        "jwt_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test_token",
        "api_key": "test_api_key_12345",
        "credentials": {"username": "testuser", "password": "testpassword"},
    }


@pytest.fixture
def mock_legal_data():
    """Mock legal compliance data for testing."""
    return {
        "disclaimer_accepted": True,
        "disclaimer_date": "2023-12-01T12:00:00Z",
        "disclaimer_version": "1.0",
        "consents": {"trading": True, "data_collection": True, "notifications": True},
    }


# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer fixture for performance testing."""
    import time

    start_time = time.time()
    yield lambda: time.time() - start_time


@pytest.fixture
def memory_profiler():
    """Memory profiler fixture."""
    import os

    import psutil

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    yield lambda: process.memory_info().rss / 1024 / 1024 - initial_memory


# Async fixtures for testing async functions
@pytest.fixture
async def async_mock_service():
    """Async mock service for testing."""
    service = AsyncMock()
    service.get_data.return_value = {"status": "success", "data": []}
    service.process_data.return_value = {"processed": True}
    return service


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    redis_mock = Mock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = True
    redis_mock.exists.return_value = False
    return redis_mock


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection for testing."""
    ws_mock = Mock()
    ws_mock.send.return_value = None
    ws_mock.recv.return_value = '{"type": "ping"}'
    ws_mock.close.return_value = None
    return ws_mock


# Test data generators
@pytest.fixture
def generate_test_data():
    """Generator function for creating test data."""

    def _generate_data(data_type: str, count: int = 100):
        if data_type == "market_data":
            return pd.DataFrame(
                {
                    "timestamp": pd.date_range("2023-01-01", periods=count, freq="1H"),
                    "symbol": "BTCUSDT",
                    "open": np.random.uniform(40000, 60000, count),
                    "high": np.random.uniform(40000, 60000, count),
                    "low": np.random.uniform(40000, 60000, count),
                    "close": np.random.uniform(40000, 60000, count),
                    "volume": np.random.uniform(1000, 10000, count),
                }
            )
        elif data_type == "predictions":
            return pd.DataFrame(
                {
                    "timestamp": pd.date_range("2023-01-01", periods=count, freq="1H"),
                    "symbol": "BTCUSDT",
                    "prediction": np.random.choice(["BULL", "BEAR", "NEUTRAL"], count),
                    "confidence": np.random.uniform(0.5, 1.0, count),
                    "bullish_prob": np.random.uniform(0, 1, count),
                    "bearish_prob": np.random.uniform(0, 1, count),
                    "neutral_prob": np.random.uniform(0, 1, count),
                }
            )
        elif data_type == "metrics":
            return pd.DataFrame(
                {
                    "epoch": range(1, count + 1),
                    "train_loss": np.random.uniform(0.01, 0.1, count),
                    "val_loss": np.random.uniform(0.01, 0.1, count),
                    "accuracy": np.random.uniform(0.7, 0.95, count),
                    "r2_score": np.random.uniform(0.6, 0.9, count),
                }
            )
        else:
            raise ValueError(f"Unknown data type: {data_type}")

    return _generate_data


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Cleanup test files after each test."""
    yield
    # Cleanup any temporary files created during tests
    import glob
    import os

    # Remove temporary test files
    for pattern in ["test_*.db", "test_*.log", "test_*.tmp"]:
        for file in glob.glob(pattern):
            try:
                os.remove(file)
            except OSError:
                pass


# Test markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "ai: mark test as AI/ML related")
    config.addinivalue_line("markers", "security: mark test as security related")
    config.addinivalue_line("markers", "legal: mark test as legal compliance related")
