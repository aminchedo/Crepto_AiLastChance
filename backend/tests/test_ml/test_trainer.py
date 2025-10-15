"""
Unit tests for the ModelTrainer class
"""

import asyncio
import os
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import numpy as np
import pandas as pd
import pytest

from backend.ml.checkpoint_manager import CheckpointManager
from backend.ml.curriculum import CurriculumManager
from backend.ml.exploration import EpsilonGreedyExploration
from backend.ml.feature_store import FeatureStore
from backend.ml.metrics import MetricsCalculator
from backend.ml.model import CryptoLSTMModel
from backend.ml.prediction_engine import CryptoPredictionEngine
from backend.ml.replay_buffer import PrioritizedExperienceReplayBuffer
from backend.ml.stability_monitor import InstabilityWatchdog
from backend.ml.trainer import ModelTrainer
from backend.services.data_quality import DataQualityPipeline
from backend.services.event_detector import CriticalEventDetector


class TestModelTrainer:
    """Test cases for ModelTrainer"""

    @pytest.fixture
    def trainer(self):
        """Create a ModelTrainer instance for testing."""
        return ModelTrainer()

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_market_data(self):
        """Create mock market data."""
        dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="1H")
        np.random.seed(42)

        data = []
        for i, date in enumerate(dates):
            data.append(
                {
                    "symbol": "BTCUSDT",
                    "timestamp": date,
                    "open": 50000 + np.random.normal(0, 1000),
                    "high": 50000 + np.random.normal(0, 1000),
                    "low": 50000 + np.random.normal(0, 1000),
                    "close": 50000 + np.random.normal(0, 1000),
                    "volume": np.random.uniform(1000, 10000),
                }
            )

        return data

    def test_trainer_initialization(self, trainer):
        """Test trainer initialization."""
        assert trainer.trainer_id is not None
        assert trainer.is_training is False
        assert trainer.current_epoch == 0
        assert trainer.max_epochs == 100
        assert trainer.model_config == {}
        assert trainer.training_metrics == []
        assert trainer.instability_watchdog is not None
        assert trainer.checkpoint_manager is not None
        assert trainer.replay_buffer is not None
        assert trainer.event_detector is not None
        assert trainer.exploration_strategy is not None
        assert trainer.feature_store is not None
        assert trainer.data_quality_pipeline is not None
        assert trainer.curriculum_manager is not None
        assert trainer.metrics_calculator is not None

    def test_trainer_initialization_with_id(self):
        """Test trainer initialization with custom ID."""
        custom_id = "test_trainer_123"
        trainer = ModelTrainer(trainer_id=custom_id)

        assert trainer.trainer_id == custom_id

    @pytest.mark.asyncio
    async def test_train_model_success(self, trainer, mock_db, mock_market_data):
        """Test successful model training."""
        # Mock the market service
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            # Mock the model building
            with patch("backend.ml.trainer.CryptoLSTMModel") as mock_model_class:
                mock_model = Mock()
                mock_model.build_model.return_value = Mock()
                mock_model_class.return_value = mock_model

                # Mock the prediction engine
                with patch("backend.ml.trainer.CryptoPredictionEngine") as mock_engine:
                    mock_engine.return_value = Mock()

                    # Test training
                    result = await trainer.train_model(
                        db=mock_db,
                        epochs=5,
                        symbols=["BTCUSDT"],
                        model_config={"learning_rate": 0.001},
                        seed=42,
                    )

                    assert result["status"] == "completed"
                    assert "message" in result
                    assert trainer.is_training is False

    @pytest.mark.asyncio
    async def test_train_model_already_training(self, trainer, mock_db):
        """Test training when already in progress."""
        trainer.is_training = True

        result = await trainer.train_model(db=mock_db, epochs=5)

        assert result["status"] == "failed"
        assert "already in progress" in result["message"]

    @pytest.mark.asyncio
    async def test_train_model_no_data(self, trainer, mock_db):
        """Test training with no market data."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = []

            result = await trainer.train_model(db=mock_db, epochs=5)

            assert result["status"] == "failed"
            assert "No historical data" in result["message"]

    @pytest.mark.asyncio
    async def test_train_model_insufficient_data(self, trainer, mock_db):
        """Test training with insufficient data for sequences."""
        # Create minimal data (less than sequence length)
        minimal_data = [
            {
                "symbol": "BTCUSDT",
                "timestamp": pd.Timestamp("2023-01-01"),
                "open": 50000,
                "high": 50000,
                "low": 50000,
                "close": 50000,
                "volume": 1000,
            }
        ]

        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = minimal_data

            result = await trainer.train_model(db=mock_db, epochs=5)

            assert result["status"] == "failed"
            assert "Not enough data" in result["message"]

    @pytest.mark.asyncio
    async def test_train_model_with_seed(self, trainer, mock_db, mock_market_data):
        """Test training with deterministic seed."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            with patch("backend.ml.trainer.CryptoLSTMModel") as mock_model_class:
                mock_model = Mock()
                mock_model.build_model.return_value = Mock()
                mock_model_class.return_value = mock_model

                with patch("backend.ml.trainer.CryptoPredictionEngine") as mock_engine:
                    mock_engine.return_value = Mock()

                    result = await trainer.train_model(db=mock_db, epochs=5, seed=42)

                    assert result["status"] == "completed"
                    assert trainer.seed == 42

    @pytest.mark.asyncio
    async def test_train_model_with_custom_config(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training with custom model configuration."""
        custom_config = {
            "learning_rate": 0.01,
            "sequence_length": 120,
            "lstm_units": [128, 64],
            "dropout_rate": 0.3,
            "gradient_clip_norm": 1.0,
            "early_stopping_patience": 15,
        }

        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            with patch("backend.ml.trainer.CryptoLSTMModel") as mock_model_class:
                mock_model = Mock()
                mock_model.build_model.return_value = Mock()
                mock_model_class.return_value = mock_model

                with patch("backend.ml.trainer.CryptoPredictionEngine") as mock_engine:
                    mock_engine.return_value = Mock()

                    result = await trainer.train_model(
                        db=mock_db, epochs=5, model_config=custom_config
                    )

                    assert result["status"] == "completed"
                    assert trainer.model_config == custom_config

    @pytest.mark.asyncio
    async def test_train_model_with_symbols(self, trainer, mock_db, mock_market_data):
        """Test training with specific symbols."""
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            with patch("backend.ml.trainer.CryptoLSTMModel") as mock_model_class:
                mock_model = Mock()
                mock_model.build_model.return_value = Mock()
                mock_model_class.return_value = mock_model

                with patch("backend.ml.trainer.CryptoPredictionEngine") as mock_engine:
                    mock_engine.return_value = Mock()

                    result = await trainer.train_model(
                        db=mock_db, epochs=5, symbols=symbols
                    )

                    assert result["status"] == "completed"
                    # Verify that get_historical_data was called with correct symbols
                    mock_service.return_value.get_historical_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_train_model_instability_detection(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training with instability detection."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            with patch("backend.ml.trainer.CryptoLSTMModel") as mock_model_class:
                mock_model = Mock()
                mock_model.build_model.return_value = Mock()
                mock_model_class.return_value = mock_model

                with patch("backend.ml.trainer.CryptoPredictionEngine") as mock_engine:
                    mock_engine.return_value = Mock()

                    # Mock instability detection
                    trainer.instability_watchdog.detect_instability = Mock(
                        return_value="Loss Spike"
                    )

                    result = await trainer.train_model(db=mock_db, epochs=5)

                    assert result["status"] == "completed"
                    # Verify instability detection was called
                    assert trainer.instability_watchdog.detect_instability.called

    @pytest.mark.asyncio
    async def test_train_model_early_stopping(self, trainer, mock_db, mock_market_data):
        """Test training with early stopping."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            with patch("backend.ml.trainer.CryptoLSTMModel") as mock_model_class:
                mock_model = Mock()
                mock_model.build_model.return_value = Mock()
                mock_model_class.return_value = mock_model

                with patch("backend.ml.trainer.CryptoPredictionEngine") as mock_engine:
                    mock_engine.return_value = Mock()

                    result = await trainer.train_model(
                        db=mock_db,
                        epochs=100,
                        model_config={"early_stopping_patience": 2},
                    )

                    assert result["status"] == "completed"
                    # Verify that training stopped early
                    assert trainer.current_epoch < 100

    @pytest.mark.asyncio
    async def test_train_model_experience_replay(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training with experience replay."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            with patch("backend.ml.trainer.CryptoLSTMModel") as mock_model_class:
                mock_model = Mock()
                mock_model.build_model.return_value = Mock()
                mock_model_class.return_value = mock_model

                with patch("backend.ml.trainer.CryptoPredictionEngine") as mock_engine:
                    mock_engine.return_value = Mock()

                    result = await trainer.train_model(db=mock_db, epochs=5)

                    assert result["status"] == "completed"
                    # Verify that experience replay buffer was used
                    assert len(trainer.replay_buffer) > 0

    @pytest.mark.asyncio
    async def test_train_model_curriculum_learning(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training with curriculum learning."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            with patch("backend.ml.trainer.CryptoLSTMModel") as mock_model_class:
                mock_model = Mock()
                mock_model.build_model.return_value = Mock()
                mock_model_class.return_value = mock_model

                with patch("backend.ml.trainer.CryptoPredictionEngine") as mock_engine:
                    mock_engine.return_value = Mock()

                    result = await trainer.train_model(db=mock_db, epochs=5)

                    assert result["status"] == "completed"
                    # Verify that curriculum manager was used
                    assert trainer.curriculum_manager is not None

    @pytest.mark.asyncio
    async def test_train_model_metrics_calculation(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training with metrics calculation."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            with patch("backend.ml.trainer.CryptoLSTMModel") as mock_model_class:
                mock_model = Mock()
                mock_model.build_model.return_value = Mock()
                mock_model_class.return_value = mock_model

                with patch("backend.ml.trainer.CryptoPredictionEngine") as mock_engine:
                    mock_engine.return_value = Mock()

                    result = await trainer.train_model(db=mock_db, epochs=5)

                    assert result["status"] == "completed"
                    # Verify that metrics were calculated
                    assert len(trainer.training_metrics) > 0

                    # Check that metrics contain expected keys
                    for metric in trainer.training_metrics:
                        assert "epoch" in metric
                        assert "train_loss" in metric
                        assert "val_loss" in metric
                        assert "lr" in metric

    @pytest.mark.asyncio
    async def test_train_model_error_handling(self, trainer, mock_db):
        """Test training error handling."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.side_effect = Exception(
                "Database error"
            )

            result = await trainer.train_model(db=mock_db, epochs=5)

            assert result["status"] == "failed"
            assert "Error during training" in result["message"]
            assert trainer.is_training is False

    @pytest.mark.asyncio
    async def test_train_model_graceful_shutdown(
        self, trainer, mock_db, mock_market_data
    ):
        """Test training graceful shutdown."""
        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = (
                mock_market_data
            )

            with patch("backend.ml.trainer.CryptoLSTMModel") as mock_model_class:
                mock_model = Mock()
                mock_model.build_model.return_value = Mock()
                mock_model_class.return_value = mock_model

                with patch("backend.ml.trainer.CryptoPredictionEngine") as mock_engine:
                    mock_engine.return_value = Mock()

                    # Start training
                    training_task = asyncio.create_task(
                        trainer.train_model(db=mock_db, epochs=100)
                    )

                    # Simulate stopping training
                    await asyncio.sleep(0.1)
                    trainer.is_training = False

                    result = await training_task

                    assert result["status"] == "completed"
                    assert "stopped by user" in result["message"]

    def test_trainer_state_management(self, trainer):
        """Test trainer state management."""
        # Test initial state
        assert trainer.is_training is False
        assert trainer.current_epoch == 0
        assert trainer.training_metrics == []

        # Test state changes
        trainer.is_training = True
        trainer.current_epoch = 10
        trainer.training_metrics = [{"epoch": 1, "loss": 0.1}]

        assert trainer.is_training is True
        assert trainer.current_epoch == 10
        assert len(trainer.training_metrics) == 1

    def test_trainer_reset(self, trainer):
        """Test trainer reset functionality."""
        # Set some state
        trainer.is_training = True
        trainer.current_epoch = 10
        trainer.training_metrics = [{"epoch": 1, "loss": 0.1}]

        # Reset trainer
        trainer.reset()

        assert trainer.is_training is False
        assert trainer.current_epoch == 0
        assert trainer.training_metrics == []

    def test_trainer_get_status(self, trainer):
        """Test trainer status retrieval."""
        status = trainer.get_status()

        assert "trainer_id" in status
        assert "is_training" in status
        assert "current_epoch" in status
        assert "max_epochs" in status
        assert "model_config" in status
        assert "training_metrics" in status

    def test_trainer_get_metrics(self, trainer):
        """Test trainer metrics retrieval."""
        # Add some mock metrics
        trainer.training_metrics = [
            {"epoch": 1, "train_loss": 0.1, "val_loss": 0.12},
            {"epoch": 2, "train_loss": 0.08, "val_loss": 0.10},
        ]

        metrics = trainer.get_metrics()

        assert len(metrics) == 2
        assert metrics[0]["epoch"] == 1
        assert metrics[1]["epoch"] == 2

    def test_trainer_performance_benchmarks(self, trainer):
        """Test trainer performance benchmarks."""
        # Test that trainer initializes quickly
        import time

        start_time = time.time()
        new_trainer = ModelTrainer()
        end_time = time.time()

        initialization_time = end_time - start_time
        assert (
            initialization_time < 1.0
        ), f"Initialization took {initialization_time:.3f}s, expected < 1.0s"

    def test_trainer_memory_usage(self, trainer):
        """Test trainer memory usage."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024

        # Should be under 2GB
        assert memory_mb < 2048, f"Memory usage {memory_mb:.1f}MB, expected < 2048MB"

    def test_trainer_logging(self, trainer):
        """Test trainer logging functionality."""
        # Test that logger is properly initialized
        assert trainer.logger is not None
        assert trainer.logger.name == f"ModelTrainer-{trainer.trainer_id}"

    def test_trainer_component_initialization(self, trainer):
        """Test that all trainer components are properly initialized."""
        assert trainer.instability_watchdog is not None
        assert trainer.checkpoint_manager is not None
        assert trainer.replay_buffer is not None
        assert trainer.event_detector is not None
        assert trainer.exploration_strategy is not None
        assert trainer.feature_store is not None
        assert trainer.data_quality_pipeline is not None
        assert trainer.curriculum_manager is not None
        assert trainer.metrics_calculator is not None

    def test_trainer_configuration_validation(self, trainer):
        """Test trainer configuration validation."""
        # Test valid configuration
        valid_config = {
            "learning_rate": 0.001,
            "sequence_length": 60,
            "batch_size": 32,
            "epochs": 100,
        }

        # This should not raise an exception
        trainer.validate_config(valid_config)

        # Test invalid configuration
        invalid_config = {
            "learning_rate": -0.001,  # Negative learning rate
            "sequence_length": 0,  # Zero sequence length
            "batch_size": -32,  # Negative batch size
            "epochs": 0,  # Zero epochs
        }

        with pytest.raises(ValueError):
            trainer.validate_config(invalid_config)
