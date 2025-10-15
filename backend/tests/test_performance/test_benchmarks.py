"""
Performance benchmarks for the BOLT AI Neural Agent System
"""

import asyncio
import os
import time
from unittest.mock import AsyncMock, Mock, patch

import numpy as np
import pandas as pd
import psutil
import pytest
import tensorflow as tf
from fastapi.testclient import TestClient

from backend.api.market import router
from backend.main import app
from backend.ml.model import CryptoLSTMModel
from backend.ml.trainer import ModelTrainer
from backend.services.market_service import MarketService


class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    @pytest.fixture
    def performance_thresholds(self):
        """Performance threshold definitions."""
        return {
            "startup_time": 5.0,  # seconds
            "prediction_latency": 0.1,  # seconds
            "ui_frame_time": 16.67,  # milliseconds (60 FPS)
            "memory_usage": 2.0,  # GB
            "training_epoch_time": 10.0,  # seconds per epoch
            "api_response_time": 1.0,  # seconds
            "database_query_time": 0.5,  # seconds
            "model_loading_time": 2.0,  # seconds
            "model_saving_time": 1.0,  # seconds
            "data_processing_time": 0.1,  # seconds per 1000 records
        }

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_model_startup_time(self, performance_thresholds):
        """Test model initialization performance."""
        start_time = time.time()

        model = CryptoLSTMModel()
        model.build_model()

        end_time = time.time()
        startup_time = end_time - start_time

        assert (
            startup_time < performance_thresholds["startup_time"]
        ), f"Model startup took {startup_time:.3f}s, expected < {performance_thresholds['startup_time']}s"

    def test_model_prediction_latency(self, performance_thresholds):
        """Test model prediction latency."""
        model = CryptoLSTMModel()
        model.build_model()

        # Create test input
        X = np.random.randn(1, 60, 10)

        # Warm up
        for _ in range(10):
            model.predict(X)

        # Measure prediction time
        start_time = time.time()

        for _ in range(100):
            prediction = model.predict(X)

        end_time = time.time()
        avg_prediction_time = (end_time - start_time) / 100

        assert (
            avg_prediction_time < performance_thresholds["prediction_latency"]
        ), f"Average prediction took {avg_prediction_time:.3f}s, expected < {performance_thresholds['prediction_latency']}s"

    def test_model_memory_usage(self, performance_thresholds):
        """Test model memory usage."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create and use model
        model = CryptoLSTMModel()
        model.build_model()

        # Make some predictions
        X = np.random.randn(100, 60, 10)
        for i in range(10):
            predictions = model.predict_batch(X)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_usage = final_memory - initial_memory

        assert (
            memory_usage < performance_thresholds["memory_usage"] * 1024
        ), f"Memory usage {memory_usage:.1f}MB, expected < {performance_thresholds['memory_usage'] * 1024}MB"

    def test_model_loading_performance(self, performance_thresholds):
        """Test model loading performance."""
        model = CryptoLSTMModel()
        model.build_model()

        # Save model
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = os.path.join(temp_dir, "test_model")
            model.save_model(model_path)

            # Test loading performance
            start_time = time.time()

            new_model = CryptoLSTMModel()
            new_model.load_model(model_path)

            end_time = time.time()
            loading_time = end_time - start_time

            assert (
                loading_time < performance_thresholds["model_loading_time"]
            ), f"Model loading took {loading_time:.3f}s, expected < {performance_thresholds['model_loading_time']}s"

    def test_model_saving_performance(self, performance_thresholds):
        """Test model saving performance."""
        model = CryptoLSTMModel()
        model.build_model()

        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = os.path.join(temp_dir, "test_model")

            start_time = time.time()

            model.save_model(model_path)

            end_time = time.time()
            saving_time = end_time - start_time

            assert (
                saving_time < performance_thresholds["model_saving_time"]
            ), f"Model saving took {saving_time:.3f}s, expected < {performance_thresholds['model_saving_time']}s"

    def test_training_epoch_performance(self, performance_thresholds):
        """Test training epoch performance."""
        trainer = ModelTrainer()

        # Create mock data
        mock_data = []
        for i in range(1000):
            mock_data.append(
                {
                    "symbol": "BTCUSDT",
                    "timestamp": pd.Timestamp("2023-01-01") + pd.Timedelta(hours=i),
                    "open": 50000 + np.random.normal(0, 1000),
                    "high": 50000 + np.random.normal(0, 1000),
                    "low": 50000 + np.random.normal(0, 1000),
                    "close": 50000 + np.random.normal(0, 1000),
                    "volume": np.random.uniform(1000, 10000),
                }
            )

        mock_db = AsyncMock()

        with patch("backend.ml.trainer.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = mock_data

            start_time = time.time()

            result = asyncio.run(
                trainer.train_model(
                    db=mock_db,
                    epochs=1,
                    symbols=["BTCUSDT"],
                    model_config={"learning_rate": 0.001},
                    seed=42,
                )
            )

            end_time = time.time()
            epoch_time = end_time - start_time

            assert result["status"] == "completed"
            assert (
                epoch_time < performance_thresholds["training_epoch_time"]
            ), f"Training epoch took {epoch_time:.3f}s, expected < {performance_thresholds['training_epoch_time']}s"

    def test_api_response_performance(self, client, performance_thresholds):
        """Test API response performance."""
        with patch("backend.api.market.MarketService") as mock_service:
            mock_service.return_value.get_historical_data.return_value = []

            start_time = time.time()

            response = client.get(
                "/api/v1/market/data?symbols=BTCUSDT&interval=1h&limit=100"
            )

            end_time = time.time()
            response_time = end_time - start_time

            assert response.status_code == 200
            assert (
                response_time < performance_thresholds["api_response_time"]
            ), f"API response took {response_time:.3f}s, expected < {performance_thresholds['api_response_time']}s"

    def test_data_processing_performance(self, performance_thresholds):
        """Test data processing performance."""
        # Create test data
        data_size = 10000
        test_data = pd.DataFrame(
            {
                "timestamp": pd.date_range("2023-01-01", periods=data_size, freq="1H"),
                "symbol": "BTCUSDT",
                "open": np.random.uniform(40000, 60000, data_size),
                "high": np.random.uniform(40000, 60000, data_size),
                "low": np.random.uniform(40000, 60000, data_size),
                "close": np.random.uniform(40000, 60000, data_size),
                "volume": np.random.uniform(1000, 10000, data_size),
            }
        )

        start_time = time.time()

        # Simulate data processing
        processed_data = test_data.copy()
        processed_data["returns"] = processed_data["close"].pct_change()
        processed_data["ma_20"] = processed_data["close"].rolling(20).mean()
        processed_data["volatility"] = processed_data["returns"].rolling(20).std()
        processed_data = processed_data.dropna()

        end_time = time.time()
        processing_time = end_time - start_time

        expected_time = performance_thresholds["data_processing_time"] * (
            data_size / 1000
        )

        assert (
            processing_time < expected_time
        ), f"Data processing took {processing_time:.3f}s, expected < {expected_time:.3f}s"

    def test_concurrent_prediction_performance(self, performance_thresholds):
        """Test concurrent prediction performance."""
        model = CryptoLSTMModel()
        model.build_model()

        def predict_batch():
            X = np.random.randn(10, 60, 10)
            return model.predict_batch(X)

        # Test concurrent predictions
        import threading
        import time

        results = []

        def prediction_thread():
            start_time = time.time()
            predictions = predict_batch()
            end_time = time.time()
            results.append(end_time - start_time)

        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=prediction_thread)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check performance
        avg_time = sum(results) / len(results)
        assert (
            avg_time < performance_thresholds["prediction_latency"] * 10
        ), f"Average concurrent prediction took {avg_time:.3f}s, expected < {performance_thresholds['prediction_latency'] * 10}s"

    def test_memory_leak_detection(self):
        """Test for memory leaks in model operations."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        model = CryptoLSTMModel()
        model.build_model()

        # Perform many operations
        for i in range(1000):
            X = np.random.randn(1, 60, 10)
            prediction = model.predict(X)

            # Force garbage collection every 100 iterations
            if i % 100 == 0:
                import gc

                gc.collect()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be minimal (under 100MB)
        assert (
            memory_increase < 100
        ), f"Memory increased by {memory_increase:.1f}MB, expected < 100MB (possible memory leak)"

    def test_cpu_usage_performance(self):
        """Test CPU usage during intensive operations."""
        model = CryptoLSTMModel()
        model.build_model()

        # Monitor CPU usage during predictions
        cpu_percentages = []

        def monitor_cpu():
            while True:
                cpu_percent = psutil.cpu_percent()
                cpu_percentages.append(cpu_percent)
                time.sleep(0.1)

        import threading

        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.daemon = True
        monitor_thread.start()

        # Perform intensive predictions
        start_time = time.time()
        for _ in range(1000):
            X = np.random.randn(1, 60, 10)
            prediction = model.predict(X)
        end_time = time.time()

        # Stop monitoring
        time.sleep(0.5)  # Let monitor collect a few more samples

        # Check CPU usage
        if cpu_percentages:
            avg_cpu = sum(cpu_percentages) / len(cpu_percentages)
            max_cpu = max(cpu_percentages)

            # CPU usage should be reasonable
            assert avg_cpu < 80, f"Average CPU usage {avg_cpu:.1f}%, expected < 80%"
            assert max_cpu < 95, f"Maximum CPU usage {max_cpu:.1f}%, expected < 95%"

    def test_scalability_performance(self):
        """Test scalability with increasing data size."""
        model = CryptoLSTMModel()
        model.build_model()

        batch_sizes = [1, 10, 50, 100]
        times = []

        for batch_size in batch_sizes:
            X = np.random.randn(batch_size, 60, 10)

            start_time = time.time()
            predictions = model.predict_batch(X)
            end_time = time.time()

            batch_time = end_time - start_time
            times.append(batch_time)

        # Check that time scales reasonably with batch size
        # Time per sample should not increase dramatically
        time_per_sample = [t / bs for t, bs in zip(times, batch_sizes)]

        # Time per sample should be relatively constant
        max_time_per_sample = max(time_per_sample)
        min_time_per_sample = min(time_per_sample)

        assert (
            max_time_per_sample / min_time_per_sample < 5
        ), f"Time per sample varies too much: {max_time_per_sample:.3f}s vs {min_time_per_sample:.3f}s"

    def test_throughput_performance(self):
        """Test system throughput performance."""
        model = CryptoLSTMModel()
        model.build_model()

        # Test throughput (predictions per second)
        batch_size = 32
        num_batches = 100

        start_time = time.time()

        for _ in range(num_batches):
            X = np.random.randn(batch_size, 60, 10)
            predictions = model.predict_batch(X)

        end_time = time.time()
        total_time = end_time - start_time

        total_predictions = num_batches * batch_size
        throughput = total_predictions / total_time

        # Should achieve at least 100 predictions per second
        assert (
            throughput > 100
        ), f"Throughput {throughput:.1f} predictions/sec, expected > 100"

    def test_latency_percentiles(self):
        """Test prediction latency percentiles."""
        model = CryptoLSTMModel()
        model.build_model()

        # Collect latency measurements
        latencies = []

        for _ in range(1000):
            X = np.random.randn(1, 60, 10)

            start_time = time.time()
            prediction = model.predict(X)
            end_time = time.time()

            latency = end_time - start_time
            latencies.append(latency)

        # Calculate percentiles
        latencies.sort()
        p50 = latencies[int(len(latencies) * 0.5)]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]

        # Check latency percentiles
        assert p50 < 0.05, f"P50 latency {p50:.3f}s, expected < 0.05s"
        assert p95 < 0.1, f"P95 latency {p95:.3f}s, expected < 0.1s"
        assert p99 < 0.2, f"P99 latency {p99:.3f}s, expected < 0.2s"

    def test_resource_utilization(self):
        """Test resource utilization during operations."""
        model = CryptoLSTMModel()
        model.build_model()

        # Monitor resources
        cpu_percentages = []
        memory_usage = []

        def monitor_resources():
            while True:
                cpu_percentages.append(psutil.cpu_percent())
                memory_usage.append(psutil.virtual_memory().percent)
                time.sleep(0.1)

        import threading

        monitor_thread = threading.Thread(target=monitor_resources)
        monitor_thread.daemon = True
        monitor_thread.start()

        # Perform operations
        for _ in range(100):
            X = np.random.randn(10, 60, 10)
            predictions = model.predict_batch(X)

        # Stop monitoring
        time.sleep(0.5)

        # Check resource utilization
        if cpu_percentages and memory_usage:
            avg_cpu = sum(cpu_percentages) / len(cpu_percentages)
            avg_memory = sum(memory_usage) / len(memory_usage)

            assert avg_cpu < 70, f"Average CPU usage {avg_cpu:.1f}%, expected < 70%"
            assert (
                avg_memory < 80
            ), f"Average memory usage {avg_memory:.1f}%, expected < 80%"

    def test_stress_test(self):
        """Test system under stress conditions."""
        model = CryptoLSTMModel()
        model.build_model()

        # Stress test with large batches and many iterations
        batch_size = 100
        num_iterations = 1000

        start_time = time.time()

        for i in range(num_iterations):
            X = np.random.randn(batch_size, 60, 10)
            predictions = model.predict_batch(X)

            # Simulate some processing delay
            if i % 100 == 0:
                time.sleep(0.001)

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete within reasonable time
        assert total_time < 300, f"Stress test took {total_time:.1f}s, expected < 300s"

        # Check memory usage after stress test
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024

        assert memory_mb < 2048, f"Memory usage {memory_mb:.1f}MB, expected < 2048MB"

    def test_performance_regression(self):
        """Test for performance regression."""
        # This test establishes baseline performance metrics
        model = CryptoLSTMModel()
        model.build_model()

        # Baseline prediction time
        X = np.random.randn(1, 60, 10)

        start_time = time.time()
        for _ in range(100):
            prediction = model.predict(X)
        end_time = time.time()

        avg_prediction_time = (end_time - start_time) / 100

        # Baseline should be under 0.1 seconds
        assert (
            avg_prediction_time < 0.1
        ), f"Baseline prediction time {avg_prediction_time:.3f}s, expected < 0.1s"

        # This test can be extended to compare against previous versions
        # and detect performance regressions
