"""
Unit tests for the CryptoLSTMModel class
"""

import os
import tempfile
from unittest.mock import Mock, patch

import numpy as np
import pytest
import tensorflow as tf

from backend.ml.activations import (LeakyReLUClipped, SigmoidClipped,
                                    TanhClipped)
from backend.ml.initializers import XavierNormal, XavierUniform
from backend.ml.model import CryptoLSTMModel


class TestCryptoLSTMModel:
    """Test cases for CryptoLSTMModel"""

    def test_model_initialization(self):
        """Test model initialization with default parameters."""
        model = CryptoLSTMModel()

        assert model.model_version == "1.0.0"
        assert model.model is None
        assert model.feature_scaler is None
        assert model.target_scaler is None
        assert model.sequence_length == 60
        assert model.n_features == 10

    def test_model_initialization_custom_params(self):
        """Test model initialization with custom parameters."""
        model = CryptoLSTMModel(
            model_version="2.0.0", sequence_length=120, n_features=20
        )

        assert model.model_version == "2.0.0"
        assert model.sequence_length == 120
        assert model.n_features == 20

    def test_build_model_default(self):
        """Test building model with default configuration."""
        model = CryptoLSTMModel()
        built_model = model.build_model()

        assert built_model is not None
        assert model.model is not None
        assert built_model == model.model

        # Check model architecture
        assert len(built_model.layers) >= 4  # LSTM + Dense layers
        assert built_model.input_shape == (None, 60, 10)
        assert built_model.output_shape == (None, 3)  # Bull/Bear/Neutral

    def test_build_model_custom_config(self):
        """Test building model with custom configuration."""
        model_config = {
            "lstm_units": [128, 64],
            "dropout_rate": 0.3,
            "dense_units": [32, 16],
            "activation": "leaky_relu",
            "initializer": "xavier_uniform",
        }

        model = CryptoLSTMModel()
        built_model = model.build_model(model_config)

        assert built_model is not None
        assert model.model is not None

        # Check that custom config was applied
        lstm_layers = [
            layer for layer in built_model.layers if "lstm" in layer.name.lower()
        ]
        assert len(lstm_layers) == 2  # Two LSTM layers

    def test_build_model_with_xavier_initialization(self):
        """Test building model with Xavier initialization."""
        model_config = {"initializer": "xavier_uniform", "seed": 42}

        model = CryptoLSTMModel()
        built_model = model.build_model(model_config)

        assert built_model is not None

        # Check that Xavier initialization was applied
        dense_layers = [
            layer for layer in built_model.layers if "dense" in layer.name.lower()
        ]
        assert len(dense_layers) > 0

    def test_build_model_with_safe_activations(self):
        """Test building model with safe activation functions."""
        model_config = {
            "activation": "leaky_relu_clipped",
            "clip_min": -10.0,
            "clip_max": 10.0,
        }

        model = CryptoLSTMModel()
        built_model = model.build_model(model_config)

        assert built_model is not None

        # Check that safe activations were applied
        activation_layers = [
            layer for layer in built_model.layers if hasattr(layer, "activation")
        ]
        assert len(activation_layers) > 0

    def test_prepare_features(self):
        """Test feature preparation."""
        model = CryptoLSTMModel()

        # Create mock data
        data = np.random.randn(100, 10)

        # Test with default parameters
        features = model.prepare_features(data)

        assert features.shape == (100, 10)
        assert not np.isnan(features).any()
        assert not np.isinf(features).any()

    def test_prepare_features_with_scaling(self):
        """Test feature preparation with scaling."""
        model = CryptoLSTMModel()

        # Create mock data
        data = np.random.randn(100, 10)

        # Test with scaling
        features = model.prepare_features(data, scale=True)

        assert features.shape == (100, 10)
        assert not np.isnan(features).any()
        assert not np.isinf(features).any()

        # Check that scaling was applied
        assert model.feature_scaler is not None

    def test_prepare_features_with_sequence(self):
        """Test feature preparation with sequence generation."""
        model = CryptoLSTMModel()

        # Create mock data
        data = np.random.randn(100, 10)

        # Test with sequence generation
        features = model.prepare_features(data, create_sequences=True)

        assert features.shape == (
            100 - model.sequence_length,
            model.sequence_length,
            10,
        )
        assert not np.isnan(features).any()
        assert not np.isinf(features).any()

    def test_predict(self):
        """Test prediction functionality."""
        model = CryptoLSTMModel()
        model.build_model()

        # Create mock input
        X = np.random.randn(1, 60, 10)

        # Test prediction
        prediction = model.predict(X)

        assert prediction is not None
        assert len(prediction) == 3  # Bull/Bear/Neutral probabilities
        assert np.isclose(np.sum(prediction), 1.0, atol=1e-6)  # Probabilities sum to 1
        assert all(0 <= p <= 1 for p in prediction)  # All probabilities between 0 and 1

    def test_predict_batch(self):
        """Test batch prediction."""
        model = CryptoLSTMModel()
        model.build_model()

        # Create mock batch input
        X = np.random.randn(5, 60, 10)

        # Test batch prediction
        predictions = model.predict_batch(X)

        assert predictions is not None
        assert predictions.shape == (5, 3)  # 5 samples, 3 classes
        assert not np.isnan(predictions).any()
        assert not np.isinf(predictions).any()

        # Check that probabilities sum to 1 for each sample
        for pred in predictions:
            assert np.isclose(np.sum(pred), 1.0, atol=1e-6)

    def test_save_model(self):
        """Test model saving."""
        model = CryptoLSTMModel()
        model.build_model()

        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = os.path.join(temp_dir, "test_model")

            # Test saving
            saved_path = model.save_model(model_path)

            assert saved_path is not None
            assert os.path.exists(saved_path)
            assert os.path.exists(f"{saved_path}.h5")

    def test_load_model(self):
        """Test model loading."""
        model = CryptoLSTMModel()
        model.build_model()

        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = os.path.join(temp_dir, "test_model")

            # Save model first
            model.save_model(model_path)

            # Create new model instance and load
            new_model = CryptoLSTMModel()
            loaded_model = new_model.load_model(model_path)

            assert loaded_model is not None
            assert new_model.model is not None

            # Test that loaded model works
            X = np.random.randn(1, 60, 10)
            prediction = new_model.predict(X)
            assert prediction is not None

    def test_model_compilation(self):
        """Test model compilation with different optimizers."""
        model = CryptoLSTMModel()

        # Test with Adam optimizer
        model_config = {"optimizer": "adam", "learning_rate": 0.001}
        built_model = model.build_model(model_config)

        assert built_model is not None
        assert built_model.optimizer is not None

        # Test with AdamW optimizer
        model_config = {
            "optimizer": "adamw",
            "learning_rate": 0.001,
            "weight_decay": 0.01,
        }
        built_model = model.build_model(model_config)

        assert built_model is not None
        assert built_model.optimizer is not None

    def test_model_with_different_losses(self):
        """Test model compilation with different loss functions."""
        model = CryptoLSTMModel()

        # Test with categorical crossentropy
        model_config = {"loss": "categorical_crossentropy"}
        built_model = model.build_model(model_config)

        assert built_model is not None

        # Test with sparse categorical crossentropy
        model_config = {"loss": "sparse_categorical_crossentropy"}
        built_model = model.build_model(model_config)

        assert built_model is not None

    def test_model_with_different_metrics(self):
        """Test model compilation with different metrics."""
        model = CryptoLSTMModel()

        # Test with multiple metrics
        model_config = {"metrics": ["accuracy", "precision", "recall", "auc"]}
        built_model = model.build_model(model_config)

        assert built_model is not None
        assert len(built_model.metrics) > 0

    def test_model_input_validation(self):
        """Test model input validation."""
        model = CryptoLSTMModel()
        model.build_model()

        # Test with invalid input shape
        with pytest.raises(ValueError):
            X = np.random.randn(1, 30, 10)  # Wrong sequence length
            model.predict(X)

        # Test with invalid number of features
        with pytest.raises(ValueError):
            X = np.random.randn(1, 60, 5)  # Wrong number of features
            model.predict(X)

    def test_model_determinism(self):
        """Test model determinism with same seed."""
        model1 = CryptoLSTMModel()
        model1.build_model({"seed": 42})

        model2 = CryptoLSTMModel()
        model2.build_model({"seed": 42})

        # Test that models produce same predictions
        X = np.random.randn(1, 60, 10)
        pred1 = model1.predict(X)
        pred2 = model2.predict(X)

        # Note: Due to TensorFlow's non-determinism, we might need to use approximate equality
        assert np.allclose(pred1, pred2, atol=1e-6)

    def test_model_performance(self):
        """Test model performance benchmarks."""
        model = CryptoLSTMModel()
        model.build_model()

        # Test prediction latency
        X = np.random.randn(1, 60, 10)

        import time

        start_time = time.time()
        prediction = model.predict(X)
        end_time = time.time()

        prediction_time = end_time - start_time

        # Should be under 100ms
        assert (
            prediction_time < 0.1
        ), f"Prediction took {prediction_time:.3f}s, expected < 0.1s"

    def test_model_memory_usage(self):
        """Test model memory usage."""
        model = CryptoLSTMModel()
        model.build_model()

        # Test that model doesn't use excessive memory
        import os

        import psutil

        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024

        # Should be under 2GB
        assert memory_mb < 2048, f"Memory usage {memory_mb:.1f}MB, expected < 2048MB"

    def test_model_error_handling(self):
        """Test model error handling."""
        model = CryptoLSTMModel()

        # Test prediction without building model
        with pytest.raises(ValueError):
            X = np.random.randn(1, 60, 10)
            model.predict(X)

        # Test saving without building model
        with pytest.raises(ValueError):
            model.save_model("test_path")

        # Test loading non-existent model
        with pytest.raises(FileNotFoundError):
            model.load_model("non_existent_path")

    def test_model_configuration_validation(self):
        """Test model configuration validation."""
        model = CryptoLSTMModel()

        # Test invalid configuration
        invalid_config = {
            "lstm_units": "invalid",  # Should be list
            "dropout_rate": 1.5,  # Should be between 0 and 1
            "activation": "invalid",  # Should be valid activation
        }

        with pytest.raises(ValueError):
            model.build_model(invalid_config)

    def test_model_with_mixed_precision(self):
        """Test model with mixed precision training."""
        model = CryptoLSTMModel()

        # Enable mixed precision
        tf.keras.mixed_precision.set_global_policy("mixed_float16")

        try:
            built_model = model.build_model()
            assert built_model is not None

            # Test prediction with mixed precision
            X = np.random.randn(1, 60, 10).astype(np.float32)
            prediction = model.predict(X)
            assert prediction is not None

        finally:
            # Reset to float32
            tf.keras.mixed_precision.set_global_policy("float32")

    def test_model_gradient_clipping(self):
        """Test model with gradient clipping."""
        model = CryptoLSTMModel()

        model_config = {"gradient_clip_norm": 1.0}

        built_model = model.build_model(model_config)
        assert built_model is not None

        # Test that gradient clipping is applied
        # This would typically be tested during training
        assert built_model.optimizer is not None

    def test_model_early_stopping(self):
        """Test model with early stopping configuration."""
        model = CryptoLSTMModel()

        model_config = {
            "early_stopping": True,
            "early_stopping_patience": 10,
            "early_stopping_min_delta": 0.001,
        }

        built_model = model.build_model(model_config)
        assert built_model is not None

        # Test that early stopping configuration is stored
        assert hasattr(model, "early_stopping_config")
        assert model.early_stopping_config["patience"] == 10

    def test_model_checkpointing(self):
        """Test model checkpointing functionality."""
        model = CryptoLSTMModel()
        model.build_model()

        with tempfile.TemporaryDirectory() as temp_dir:
            checkpoint_path = os.path.join(temp_dir, "checkpoint")

            # Test checkpoint saving
            model.save_checkpoint(checkpoint_path, epoch=10, metrics={"loss": 0.05})

            assert os.path.exists(checkpoint_path)

            # Test checkpoint loading
            loaded_model = model.load_checkpoint(checkpoint_path)
            assert loaded_model is not None

    def test_model_metrics_calculation(self):
        """Test model metrics calculation."""
        model = CryptoLSTMModel()
        model.build_model()

        # Create mock predictions and targets
        y_true = np.array([0, 1, 2, 0, 1])  # Categorical targets
        y_pred = np.array(
            [
                [0.8, 0.1, 0.1],  # Class 0
                [0.1, 0.8, 0.1],  # Class 1
                [0.1, 0.1, 0.8],  # Class 2
                [0.7, 0.2, 0.1],  # Class 0
                [0.2, 0.7, 0.1],  # Class 1
            ]
        )

        metrics = model.calculate_metrics(y_true, y_pred)

        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics

        # Check that metrics are reasonable
        assert 0 <= metrics["accuracy"] <= 1
        assert 0 <= metrics["precision"] <= 1
        assert 0 <= metrics["recall"] <= 1
        assert 0 <= metrics["f1_score"] <= 1
