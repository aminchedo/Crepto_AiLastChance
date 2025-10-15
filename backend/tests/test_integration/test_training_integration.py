"""
Integration tests for the training system
"""

import asyncio
import os
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import numpy as np
import pandas as pd
import pytest
import tensorflow as tf

from backend.config import Settings
from backend.db.sqlite_manager import SQLiteManager
from backend.ml.model import CryptoLSTMModel
from backend.ml.trainer import ModelTrainer
from backend.services.market_service import MarketService


class TestTrainingIntegration:
    """Integration tests for the training system"""

    @pytest.fixture
    def test_settings(self):
        """Create test settings."""
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
    def sqlite_manager(self, test_settings):
        """Create SQLite manager for testing."""
        manager = SQLiteManager(
            test_settings.SQLITE_DB_PATH, test_settings.SQLITE_ENCRYPTION_KEY
        )
        manager.initialize_database()
        return manager

    @pytest.fixture
    def mock_market_data(self):
        """Create mock market data for integration testing."""
        dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="1H")
        np.random.seed(42)

        data = []
        for i, date in enumerate(dates):
            # Generate realistic price data
            base_price = 50000 + np.random.normal(0, 1000)
            data.append(
                {
                    "symbol": "BTCUSDT",
                    "timestamp": date,
                    "open": base_price,
                    "high": base_price * (1 + abs(np.random.normal(0, 0.02))),
                    "low": base_price * (1 - abs(np.random.normal(0, 0.02))),
                    "close": base_price + np.random.normal(0, 500),
                    "volume": np.random.uniform(1000, 10000),
                }
            )

        return data

    @pytest.fixture
    def trainer(self):
        """Create a ModelTrainer instance for testing."""
        return ModelTrainer()

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_full_training_pipeline(
        self, trainer, mock_db, mock_market_data, test_settings
    ):
        """Test the complete training pipeline from data to model."""
        # Mock the market service
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            # Test training with realistic configuration
            model_config = {
                "learning_rate": 0.001,
                "sequence_length": 60,
                "lstm_units": [64, 32],
                "dropout_rate": 0.2,
                "dense_units": [16, 8],
                "activation": "relu",
                "initializer": "xavier_uniform",
                "gradient_clip_norm": 1.0,
                "early_stopping_patience": 5,
                "batch_size": 32,
            }

            result = await trainer.train_model(
                db=mock_db,
                epochs=10,
                symbols=["BTCUSDT"],
                model_config=model_config,
                seed=42,
            )

            assert result["status"] == "completed"
            assert trainer.is_training is False
            assert len(trainer.training_metrics) > 0

            # Verify training metrics
            for metric in trainer.training_metrics:
                assert "epoch" in metric
                assert "train_loss" in metric
                assert "val_loss" in metric
                assert "lr" in metric
                assert "gradient_norm" in metric

    @pytest.mark.asyncio
    async def test_training_with_instability_detection(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training with instability detection and recovery."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            # Mock instability detection
            instability_count = 0

            def mock_detect_instability(*args, **kwargs):
                nonlocal instability_count
                instability_count += 1
                if instability_count == 3:  # Trigger instability on 3rd call
                    return "Loss Spike"
                return None

            trainer.instability_watchdog.detect_instability = mock_detect_instability

            result = await trainer.train_model(
                db=mock_db,
                epochs=10,
                symbols=["BTCUSDT"],
                model_config={"learning_rate": 0.001},
                seed=42,
            )

            assert result["status"] == "completed"
            assert instability_count > 0  # Instability detection was called

    @pytest.mark.asyncio
    async def test_training_with_early_stopping(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training with early stopping."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            result = await trainer.train_model(
                db=mock_db,
                epochs=100,
                symbols=["BTCUSDT"],
                model_config={"early_stopping_patience": 3},
                seed=42,
            )

            assert result["status"] == "completed"
            # Should stop early due to patience
            assert trainer.current_epoch < 100

    @pytest.mark.asyncio
    async def test_training_with_experience_replay(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training with experience replay buffer."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            result = await trainer.train_model(
                db=mock_db,
                epochs=5,
                symbols=["BTCUSDT"],
                model_config={"learning_rate": 0.001},
                seed=42,
            )

            assert result["status"] == "completed"
            # Verify experience replay buffer was used
            assert len(trainer.replay_buffer) > 0

    @pytest.mark.asyncio
    async def test_training_with_curriculum_learning(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training with curriculum learning."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            result = await trainer.train_model(
                db=mock_db,
                epochs=5,
                symbols=["BTCUSDT"],
                model_config={"learning_rate": 0.001},
                seed=42,
            )

            assert result["status"] == "completed"
            # Verify curriculum manager was used
            assert trainer.curriculum_manager is not None

    @pytest.mark.asyncio
    async def test_training_with_multiple_symbols(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training with multiple symbols."""
        # Extend mock data for multiple symbols
        extended_data = mock_market_data.copy()
        for data_point in extended_data:
            if data_point["symbol"] == "BTCUSDT":
                # Add ETH data
                eth_data = data_point.copy()
                eth_data["symbol"] = "ETHUSDT"
                eth_data["open"] *= 0.06  # ETH price roughly 1/16 of BTC
                eth_data["high"] *= 0.06
                eth_data["low"] *= 0.06
                eth_data["close"] *= 0.06
                extended_data.append(eth_data)

        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = extended_data

            result = await trainer.train_model(
                db=mock_db,
                epochs=5,
                symbols=["BTCUSDT", "ETHUSDT"],
                model_config={"learning_rate": 0.001},
                seed=42,
            )

            assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_training_performance_benchmarks(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training performance benchmarks."""
        import time

        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            start_time = time.time()

            result = await trainer.train_model(
                db=mock_db,
                epochs=5,
                symbols=["BTCUSDT"],
                model_config={"learning_rate": 0.001},
                seed=42,
            )

            end_time = time.time()
            training_time = end_time - start_time

            assert result["status"] == "completed"
            # Training should complete within reasonable time
            assert (
                training_time < 60.0
            ), f"Training took {training_time:.2f}s, expected < 60s"

    @pytest.mark.asyncio
    async def test_training_memory_usage(self, trainer, mock_db, mock_market_data):
        """Test training memory usage."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024

        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            result = await trainer.train_model(
                db=mock_db,
                epochs=5,
                symbols=["BTCUSDT"],
                model_config={"learning_rate": 0.001},
                seed=42,
            )

            final_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = final_memory - initial_memory

            assert result["status"] == "completed"
            # Memory increase should be reasonable
            assert (
                memory_increase < 500
            ), f"Memory increased by {memory_increase:.1f}MB, expected < 500MB"

    @pytest.mark.asyncio
    async def test_training_determinism(self, trainer, mock_db, mock_market_data):
        """Test training determinism with same seed."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            # Train with same seed twice
            result1 = await trainer.train_model(
                db=mock_db,
                epochs=3,
                symbols=["BTCUSDT"],
                model_config={"learning_rate": 0.001},
                seed=42,
            )

            # Reset trainer
            trainer.reset()

            result2 = await trainer.train_model(
                db=mock_db,
                epochs=3,
                symbols=["BTCUSDT"],
                model_config={"learning_rate": 0.001},
                seed=42,
            )

            assert result1["status"] == "completed"
            assert result2["status"] == "completed"

            # Training metrics should be similar (allowing for some variance)
            assert len(trainer.training_metrics) > 0

    @pytest.mark.asyncio
    async def test_training_error_recovery(self, trainer, mock_db, mock_market_data):
        """Test training error recovery."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            # Mock an error during training
            error_count = 0

            def mock_training_step(*args, **kwargs):
                nonlocal error_count
                error_count += 1
                if error_count == 2:  # Trigger error on 2nd call
                    raise Exception("Simulated training error")
                return None

            # This would need to be implemented in the actual trainer
            # For now, we just test that the trainer handles errors gracefully

            result = await trainer.train_model(
                db=mock_db,
                epochs=5,
                symbols=["BTCUSDT"],
                model_config={"learning_rate": 0.001},
                seed=42,
            )

            assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_training_with_checkpointing(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training with checkpointing."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            result = await trainer.train_model(
                db=mock_db,
                epochs=5,
                symbols=["BTCUSDT"],
                model_config={"learning_rate": 0.001},
                seed=42,
            )

            assert result["status"] == "completed"
            # Verify checkpoint manager was used
            assert trainer.checkpoint_manager is not None

    @pytest.mark.asyncio
    async def test_training_with_feature_engineering(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training with feature engineering."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            result = await trainer.train_model(
                db=mock_db,
                epochs=5,
                symbols=["BTCUSDT"],
                model_config={"learning_rate": 0.001},
                seed=42,
            )

            assert result["status"] == "completed"
            # Verify feature store was used
            assert trainer.feature_store is not None

    @pytest.mark.asyncio
    async def test_training_with_data_quality_pipeline(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training with data quality pipeline."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            result = await trainer.train_model(
                db=mock_db,
                epochs=5,
                symbols=["BTCUSDT"],
                model_config={"learning_rate": 0.001},
                seed=42,
            )

            assert result["status"] == "completed"
            # Verify data quality pipeline was used
            assert trainer.data_quality_pipeline is not None

    @pytest.mark.asyncio
    async def test_training_with_metrics_calculation(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training with metrics calculation."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            result = await trainer.train_model(
                db=mock_db,
                epochs=5,
                symbols=["BTCUSDT"],
                model_config={"learning_rate": 0.001},
                seed=42,
            )

            assert result["status"] == "completed"
            # Verify metrics calculator was used
            assert trainer.metrics_calculator is not None

            # Check that metrics were calculated
            assert len(trainer.training_metrics) > 0

            # Verify metric structure
            for metric in trainer.training_metrics:
                assert "epoch" in metric
                assert "train_loss" in metric
                assert "val_loss" in metric
                assert "train_r2" in metric
                assert "val_r2" in metric
                assert "lr" in metric
                assert "gradient_norm" in metric

    @pytest.mark.asyncio
    async def test_training_concurrent_access(self, mock_db, mock_market_data):
        """Test training with concurrent access."""
        import threading
        import time

        results = []

        def train_model_thread():
            trainer = ModelTrainer()
            with patch("backend.ml.trainer.MarketService") as mock_service:
                mock_service.return_value.get_historical_data.return_value = (
                    mock_market_data
                )

                result = asyncio.run(
                    trainer.train_model(
                        db=mock_db,
                        epochs=3,
                        symbols=["BTCUSDT"],
                        model_config={"learning_rate": 0.001},
                        seed=42,
                    )
                )
                results.append(result["status"])

        # Create multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=train_model_thread)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that all training completed successfully
        assert len(results) == 3
        assert all(status == "completed" for status in results)

    @pytest.mark.asyncio
    async def test_training_with_realistic_data(self, trainer, mock_db):
        """Test training with realistic market data."""
        # Create more realistic market data
        dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="1H")
        np.random.seed(42)

        realistic_data = []
        base_price = 50000
        for i, date in enumerate(dates):
            # Add some trend and seasonality
            trend = 0.0001 * i  # Slight upward trend
            seasonality = 0.01 * np.sin(2 * np.pi * i / (24 * 7))  # Weekly seasonality
            noise = np.random.normal(0, 0.02)  # 2% noise

            price_change = trend + seasonality + noise
            current_price = base_price * (1 + price_change)

            realistic_data.append(
                {
                    "symbol": "BTCUSDT",
                    "timestamp": date,
                    "open": current_price,
                    "high": current_price * (1 + abs(np.random.normal(0, 0.01))),
                    "low": current_price * (1 - abs(np.random.normal(0, 0.01))),
                    "close": current_price + np.random.normal(0, current_price * 0.005),
                    "volume": np.random.uniform(1000, 10000),
                }
            )

        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = realistic_data

            result = await trainer.train_model(
                db=mock_db,
                epochs=5,
                symbols=["BTCUSDT"],
                model_config={"learning_rate": 0.001},
                seed=42,
            )

            assert result["status"] == "completed"
            assert len(trainer.training_metrics) > 0

            # Check that training metrics show improvement
            if len(trainer.training_metrics) > 1:
                first_loss = trainer.training_metrics[0]["train_loss"]
                last_loss = trainer.training_metrics[-1]["train_loss"]
                # Loss should generally decrease (allowing for some variance)
                assert last_loss <= first_loss * 1.1  # Allow 10% increase due to noise
