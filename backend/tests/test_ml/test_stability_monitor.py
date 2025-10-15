"""
Unit tests for the InstabilityWatchdog class
"""

from unittest.mock import Mock, patch

import numpy as np
import pytest
import tensorflow as tf

from backend.ml.stability_monitor import InstabilityWatchdog


class TestInstabilityWatchdog:
    """Test cases for InstabilityWatchdog"""

    @pytest.fixture
    def watchdog(self):
        """Create an InstabilityWatchdog instance for testing."""
        return InstabilityWatchdog()

    @pytest.fixture
    def custom_watchdog(self):
        """Create a custom InstabilityWatchdog instance."""
        return InstabilityWatchdog(
            loss_spike_threshold=2.0,
            gradient_spike_factor=2.0,
            ema_smoothing=0.2,
            min_loss_for_spike=0.005,
        )

    def test_watchdog_initialization(self, watchdog):
        """Test watchdog initialization with default parameters."""
        assert watchdog.loss_spike_threshold == 3.0
        assert watchdog.gradient_spike_factor == 2.5
        assert watchdog.ema_smoothing == 0.1
        assert watchdog.min_loss_for_spike == 0.01
        assert watchdog.ema_loss is None
        assert watchdog.ema_gradient_norm is None

    def test_watchdog_initialization_custom(self, custom_watchdog):
        """Test watchdog initialization with custom parameters."""
        assert custom_watchdog.loss_spike_threshold == 2.0
        assert custom_watchdog.gradient_spike_factor == 2.0
        assert custom_watchdog.ema_smoothing == 0.2
        assert custom_watchdog.min_loss_for_spike == 0.005

    def test_detect_instability_nan_loss(self, watchdog):
        """Test detection of NaN loss."""
        result = watchdog.detect_instability(
            current_loss=tf.constant(float("nan")), current_gradient_norm=1.0
        )

        assert result == "NaN/Inf Loss"

    def test_detect_instability_inf_loss(self, watchdog):
        """Test detection of infinite loss."""
        result = watchdog.detect_instability(
            current_loss=tf.constant(float("inf")), current_gradient_norm=1.0
        )

        assert result == "NaN/Inf Loss"

    def test_detect_instability_loss_spike(self, watchdog):
        """Test detection of loss spike."""
        # First call to initialize EMA
        watchdog.detect_instability(current_loss=0.01, current_gradient_norm=1.0)

        # Second call with spike
        result = watchdog.detect_instability(
            current_loss=0.05, current_gradient_norm=1.0  # 5x the EMA (0.01)
        )

        assert result == "Loss Spike"

    def test_detect_instability_gradient_spike(self, watchdog):
        """Test detection of gradient norm spike."""
        # First call to initialize EMA
        watchdog.detect_instability(current_loss=0.01, current_gradient_norm=1.0)

        # Second call with gradient spike
        result = watchdog.detect_instability(
            current_loss=0.01, current_gradient_norm=3.0  # 3x the EMA (1.0)
        )

        assert result == "Gradient Norm Spike"

    def test_detect_instability_validation_collapse(self, watchdog):
        """Test detection of validation collapse."""
        previous_metrics = {"r2_score": 0.8}
        current_metrics = {"r2_score": 0.3}  # Significant drop

        result = watchdog.detect_instability(
            current_loss=0.01,
            current_gradient_norm=1.0,
            validation_metrics=current_metrics,
            previous_validation_metrics=previous_metrics,
        )

        assert result == "Validation Collapse"

    def test_detect_instability_no_instability(self, watchdog):
        """Test no instability detection with normal values."""
        result = watchdog.detect_instability(
            current_loss=0.01, current_gradient_norm=1.0
        )

        assert result is None

    def test_detect_instability_ema_initialization(self, watchdog):
        """Test EMA initialization on first call."""
        assert watchdog.ema_loss is None
        assert watchdog.ema_gradient_norm is None

        watchdog.detect_instability(current_loss=0.01, current_gradient_norm=1.0)

        assert watchdog.ema_loss == 0.01
        assert watchdog.ema_gradient_norm == 1.0

    def test_detect_instability_ema_smoothing(self, watchdog):
        """Test EMA smoothing calculation."""
        # First call
        watchdog.detect_instability(current_loss=0.01, current_gradient_norm=1.0)

        # Second call
        watchdog.detect_instability(current_loss=0.02, current_gradient_norm=2.0)

        # Check EMA calculation
        expected_ema_loss = 0.1 * 0.02 + 0.9 * 0.01
        expected_ema_gradient = 0.1 * 2.0 + 0.9 * 1.0

        assert abs(watchdog.ema_loss - expected_ema_loss) < 1e-6
        assert abs(watchdog.ema_gradient_norm - expected_ema_gradient) < 1e-6

    def test_detect_instability_loss_spike_threshold(self, watchdog):
        """Test loss spike threshold calculation."""
        # Initialize with low loss
        watchdog.detect_instability(current_loss=0.01, current_gradient_norm=1.0)

        # Test loss just below threshold
        result = watchdog.detect_instability(
            current_loss=0.029, current_gradient_norm=1.0  # Just below 3x threshold
        )

        assert result is None

        # Test loss above threshold
        result = watchdog.detect_instability(
            current_loss=0.031, current_gradient_norm=1.0  # Just above 3x threshold
        )

        assert result == "Loss Spike"

    def test_detect_instability_gradient_spike_threshold(self, watchdog):
        """Test gradient spike threshold calculation."""
        # Initialize with normal gradient
        watchdog.detect_instability(current_loss=0.01, current_gradient_norm=1.0)

        # Test gradient just below threshold
        result = watchdog.detect_instability(
            current_loss=0.01, current_gradient_norm=2.4  # Just below 2.5x threshold
        )

        assert result is None

        # Test gradient above threshold
        result = watchdog.detect_instability(
            current_loss=0.01, current_gradient_norm=2.6  # Just above 2.5x threshold
        )

        assert result == "Gradient Norm Spike"

    def test_detect_instability_min_loss_for_spike(self, watchdog):
        """Test minimum loss threshold for spike detection."""
        # Initialize with very low loss
        watchdog.detect_instability(
            current_loss=0.005, current_gradient_norm=1.0  # Below min_loss_for_spike
        )

        # Test spike detection with low loss
        result = watchdog.detect_instability(
            current_loss=0.02,  # 4x the EMA but below min_loss_for_spike
            current_gradient_norm=1.0,
        )

        assert result is None  # Should not detect spike due to min_loss_for_spike

    def test_detect_instability_validation_metrics_missing(self, watchdog):
        """Test handling of missing validation metrics."""
        result = watchdog.detect_instability(
            current_loss=0.01,
            current_gradient_norm=1.0,
            validation_metrics=None,
            previous_validation_metrics=None,
        )

        assert result is None

    def test_detect_instability_validation_metrics_partial(self, watchdog):
        """Test handling of partial validation metrics."""
        # Test with missing r2_score
        previous_metrics = {"accuracy": 0.8}
        current_metrics = {"accuracy": 0.3}

        result = watchdog.detect_instability(
            current_loss=0.01,
            current_gradient_norm=1.0,
            validation_metrics=current_metrics,
            previous_validation_metrics=previous_metrics,
        )

        assert result is None  # Should not detect collapse without r2_score

    def test_detect_instability_validation_collapse_threshold(self, watchdog):
        """Test validation collapse threshold calculation."""
        previous_metrics = {"r2_score": 0.8}

        # Test drop just below threshold
        current_metrics = {"r2_score": 0.41}  # 0.8 * 0.5 = 0.4, just above
        result = watchdog.detect_instability(
            current_loss=0.01,
            current_gradient_norm=1.0,
            validation_metrics=current_metrics,
            previous_validation_metrics=previous_metrics,
        )

        assert result is None

        # Test drop above threshold
        current_metrics = {"r2_score": 0.39}  # Just below 0.4
        result = watchdog.detect_instability(
            current_loss=0.01,
            current_gradient_norm=1.0,
            validation_metrics=current_metrics,
            previous_validation_metrics=previous_metrics,
        )

        assert result == "Validation Collapse"

    def test_detect_instability_validation_collapse_min_r2(self, watchdog):
        """Test validation collapse minimum R2 threshold."""
        previous_metrics = {"r2_score": 0.8}

        # Test with R2 above minimum threshold
        current_metrics = {"r2_score": 0.15}  # Above 0.1
        result = watchdog.detect_instability(
            current_loss=0.01,
            current_gradient_norm=1.0,
            validation_metrics=current_metrics,
            previous_validation_metrics=previous_metrics,
        )

        assert result is None

        # Test with R2 below minimum threshold
        current_metrics = {"r2_score": 0.05}  # Below 0.1
        result = watchdog.detect_instability(
            current_loss=0.01,
            current_gradient_norm=1.0,
            validation_metrics=current_metrics,
            previous_validation_metrics=previous_metrics,
        )

        assert result == "Validation Collapse"

    def test_reset_state(self, watchdog):
        """Test watchdog state reset."""
        # Initialize state
        watchdog.detect_instability(current_loss=0.01, current_gradient_norm=1.0)

        assert watchdog.ema_loss is not None
        assert watchdog.ema_gradient_norm is not None

        # Reset state
        watchdog.reset_state()

        assert watchdog.ema_loss is None
        assert watchdog.ema_gradient_norm is None

    def test_custom_parameters(self, custom_watchdog):
        """Test watchdog with custom parameters."""
        # Test loss spike with custom threshold
        custom_watchdog.detect_instability(
            current_loss=0.005, current_gradient_norm=1.0
        )

        result = custom_watchdog.detect_instability(
            current_loss=0.012, current_gradient_norm=1.0  # 2.4x the EMA (0.005)
        )

        assert result is None  # Below custom threshold (2.0)

        result = custom_watchdog.detect_instability(
            current_loss=0.013, current_gradient_norm=1.0  # 2.6x the EMA (0.005)
        )

        assert result == "Loss Spike"  # Above custom threshold (2.0)

    def test_performance_benchmarks(self, watchdog):
        """Test watchdog performance benchmarks."""
        import time

        # Test detection speed
        start_time = time.time()

        for _ in range(1000):
            watchdog.detect_instability(current_loss=0.01, current_gradient_norm=1.0)

        end_time = time.time()
        detection_time = end_time - start_time

        # Should be fast (under 1 second for 1000 calls)
        assert (
            detection_time < 1.0
        ), f"Detection took {detection_time:.3f}s, expected < 1.0s"

    def test_memory_usage(self, watchdog):
        """Test watchdog memory usage."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024

        # Run many detections
        for _ in range(10000):
            watchdog.detect_instability(current_loss=0.01, current_gradient_norm=1.0)

        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory

        # Memory increase should be minimal (under 10MB)
        assert (
            memory_increase < 10
        ), f"Memory increased by {memory_increase:.1f}MB, expected < 10MB"

    def test_edge_cases(self, watchdog):
        """Test edge cases and boundary conditions."""
        # Test with zero loss
        result = watchdog.detect_instability(
            current_loss=0.0, current_gradient_norm=1.0
        )

        assert result is None

        # Test with zero gradient norm
        result = watchdog.detect_instability(
            current_loss=0.01, current_gradient_norm=0.0
        )

        assert result is None

        # Test with very large values
        result = watchdog.detect_instability(
            current_loss=1e6, current_gradient_norm=1e6
        )

        assert result is None  # First call, no spike detected yet

    def test_concurrent_access(self, watchdog):
        """Test watchdog with concurrent access."""
        import threading
        import time

        results = []

        def detect_instability_thread():
            for i in range(100):
                result = watchdog.detect_instability(
                    current_loss=0.01 + i * 0.001, current_gradient_norm=1.0 + i * 0.01
                )
                results.append(result)
                time.sleep(0.001)

        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=detect_instability_thread)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that all detections completed
        assert len(results) == 500  # 5 threads * 100 detections each

    def test_logging_integration(self, watchdog):
        """Test watchdog logging integration."""
        with patch("backend.ml.stability_monitor.logger") as mock_logger:
            # Test normal detection (no logging)
            watchdog.detect_instability(current_loss=0.01, current_gradient_norm=1.0)

            # Test instability detection (should log)
            watchdog.detect_instability(
                current_loss=0.05, current_gradient_norm=1.0  # Spike
            )

            # Verify warning was logged
            mock_logger.warning.assert_called()

            # Test reset (should log)
            watchdog.reset_state()

            # Verify info was logged
            mock_logger.info.assert_called()

    def test_integration_with_tensorflow(self, watchdog):
        """Test integration with TensorFlow tensors."""
        # Test with TensorFlow tensors
        loss_tensor = tf.constant(0.01)
        gradient_tensor = tf.constant(1.0)

        result = watchdog.detect_instability(
            current_loss=loss_tensor, current_gradient_norm=gradient_tensor
        )

        assert result is None

        # Test with NaN tensor
        nan_tensor = tf.constant(float("nan"))

        result = watchdog.detect_instability(
            current_loss=nan_tensor, current_gradient_norm=gradient_tensor
        )

        assert result == "NaN/Inf Loss"

    def test_state_persistence(self, watchdog):
        """Test that watchdog state persists across calls."""
        # First call
        watchdog.detect_instability(current_loss=0.01, current_gradient_norm=1.0)

        initial_ema_loss = watchdog.ema_loss
        initial_ema_gradient = watchdog.ema_gradient_norm

        # Second call
        watchdog.detect_instability(current_loss=0.02, current_gradient_norm=2.0)

        # State should have updated
        assert watchdog.ema_loss != initial_ema_loss
        assert watchdog.ema_gradient_norm != initial_ema_gradient

        # State should persist
        assert watchdog.ema_loss is not None
        assert watchdog.ema_gradient_norm is not None
