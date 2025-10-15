"""
Prometheus metrics for BOLT AI Neural Agent System
"""

import time
from typing import Any, Dict, Optional

import structlog
from prometheus_client import (CONTENT_TYPE_LATEST, CollectorRegistry, Counter,
                               Gauge, Histogram, Info, Summary,
                               generate_latest)
from prometheus_client.exposition import make_wsgi_app

logger = structlog.get_logger(__name__)


class MetricsCollector:
    """Prometheus metrics collector"""

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        self._setup_metrics()
        self._setup_wsgi_app()

    def _setup_metrics(self):
        """Setup Prometheus metrics"""

        # Application info
        self.app_info = Info(
            "bolt_ai_app_info", "Application information", registry=self.registry
        )
        self.app_info.info(
            {
                "version": "1.0.0",
                "name": "BOLT AI Neural Agent System",
                "environment": "production",
            }
        )

        # System metrics
        self.cpu_usage = Gauge(
            "bolt_ai_cpu_usage_percent", "CPU usage percentage", registry=self.registry
        )

        self.memory_usage = Gauge(
            "bolt_ai_memory_usage_bytes",
            "Memory usage in bytes",
            registry=self.registry,
        )

        self.memory_available = Gauge(
            "bolt_ai_memory_available_bytes",
            "Available memory in bytes",
            registry=self.registry,
        )

        self.disk_usage = Gauge(
            "bolt_ai_disk_usage_percent",
            "Disk usage percentage",
            registry=self.registry,
        )

        # Training metrics
        self.training_epochs = Counter(
            "bolt_ai_training_epochs_total",
            "Total number of training epochs",
            ["trainer_id", "model_version"],
            registry=self.registry,
        )

        self.training_loss = Gauge(
            "bolt_ai_training_loss",
            "Current training loss",
            ["trainer_id", "model_version"],
            registry=self.registry,
        )

        self.training_val_loss = Gauge(
            "bolt_ai_training_val_loss",
            "Current validation loss",
            ["trainer_id", "model_version"],
            registry=self.registry,
        )

        self.training_accuracy = Gauge(
            "bolt_ai_training_accuracy",
            "Current training accuracy",
            ["trainer_id", "model_version"],
            registry=self.registry,
        )

        self.training_val_accuracy = Gauge(
            "bolt_ai_training_val_accuracy",
            "Current validation accuracy",
            ["trainer_id", "model_version"],
            registry=self.registry,
        )

        self.training_learning_rate = Gauge(
            "bolt_ai_training_learning_rate",
            "Current learning rate",
            ["trainer_id", "model_version"],
            registry=self.registry,
        )

        self.training_gradient_norm = Gauge(
            "bolt_ai_training_gradient_norm",
            "Current gradient norm",
            ["trainer_id", "model_version"],
            registry=self.registry,
        )

        self.training_duration = Histogram(
            "bolt_ai_training_duration_seconds",
            "Training duration in seconds",
            ["trainer_id", "model_version"],
            buckets=[1, 5, 10, 30, 60, 300, 600, 1800, 3600],
            registry=self.registry,
        )

        self.training_batch_duration = Histogram(
            "bolt_ai_training_batch_duration_seconds",
            "Training batch duration in seconds",
            ["trainer_id", "model_version"],
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30],
            registry=self.registry,
        )

        # Prediction metrics
        self.predictions_total = Counter(
            "bolt_ai_predictions_total",
            "Total number of predictions",
            ["symbol", "model_version"],
            registry=self.registry,
        )

        self.prediction_latency = Histogram(
            "bolt_ai_prediction_latency_seconds",
            "Prediction latency in seconds",
            ["symbol", "model_version"],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5],
            registry=self.registry,
        )

        self.prediction_confidence = Histogram(
            "bolt_ai_prediction_confidence",
            "Prediction confidence score",
            ["symbol", "model_version"],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry,
        )

        self.prediction_uncertainty = Histogram(
            "bolt_ai_prediction_uncertainty",
            "Prediction uncertainty score",
            ["symbol", "model_version"],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry,
        )

        # API metrics
        self.api_requests_total = Counter(
            "bolt_ai_api_requests_total",
            "Total number of API requests",
            ["method", "endpoint", "status_code"],
            registry=self.registry,
        )

        self.api_request_duration = Histogram(
            "bolt_ai_api_request_duration_seconds",
            "API request duration in seconds",
            ["method", "endpoint"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10],
            registry=self.registry,
        )

        # Error metrics
        self.errors_total = Counter(
            "bolt_ai_errors_total",
            "Total number of errors",
            ["error_type", "component"],
            registry=self.registry,
        )

        # Instability metrics
        self.instability_events_total = Counter(
            "bolt_ai_instability_events_total",
            "Total number of instability events",
            ["trainer_id", "reason"],
            registry=self.registry,
        )

        self.checkpoint_saves_total = Counter(
            "bolt_ai_checkpoint_saves_total",
            "Total number of checkpoint saves",
            ["trainer_id", "model_version"],
            registry=self.registry,
        )

        self.checkpoint_restores_total = Counter(
            "bolt_ai_checkpoint_restores_total",
            "Total number of checkpoint restores",
            ["trainer_id", "model_version"],
            registry=self.registry,
        )

        # Experience replay metrics
        self.experience_buffer_size = Gauge(
            "bolt_ai_experience_buffer_size",
            "Current experience buffer size",
            ["trainer_id"],
            registry=self.registry,
        )

        self.experience_samples_total = Counter(
            "bolt_ai_experience_samples_total",
            "Total number of experience samples",
            ["trainer_id"],
            registry=self.registry,
        )

        # Market data metrics
        self.market_data_updates_total = Counter(
            "bolt_ai_market_data_updates_total",
            "Total number of market data updates",
            ["symbol", "source"],
            registry=self.registry,
        )

        self.market_data_latency = Histogram(
            "bolt_ai_market_data_latency_seconds",
            "Market data latency in seconds",
            ["symbol", "source"],
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60],
            registry=self.registry,
        )

        # Backtesting metrics
        self.backtests_total = Counter(
            "bolt_ai_backtests_total",
            "Total number of backtests",
            ["symbol", "timeframe"],
            registry=self.registry,
        )

        self.backtest_accuracy = Histogram(
            "bolt_ai_backtest_accuracy",
            "Backtest directional accuracy",
            ["symbol", "timeframe"],
            buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry,
        )

        self.backtest_sharpe_ratio = Histogram(
            "bolt_ai_backtest_sharpe_ratio",
            "Backtest Sharpe ratio",
            ["symbol", "timeframe"],
            buckets=[-2, -1, 0, 1, 2, 3, 5, 10],
            registry=self.registry,
        )

        logger.info("Prometheus metrics initialized")

    def _setup_wsgi_app(self):
        """Setup WSGI app for metrics endpoint"""
        self.wsgi_app = make_wsgi_app(self.registry)

    def update_system_metrics(
        self,
        cpu_usage: float,
        memory_usage: float,
        memory_available: float,
        disk_usage: float,
    ):
        """Update system metrics"""
        self.cpu_usage.set(cpu_usage)
        self.memory_usage.set(memory_usage)
        self.memory_available.set(memory_available)
        self.disk_usage.set(disk_usage)

    def update_training_metrics(
        self,
        trainer_id: str,
        model_version: str,
        epoch: int,
        loss: float,
        val_loss: float,
        accuracy: float,
        val_accuracy: float,
        learning_rate: float,
        gradient_norm: float,
        batch_duration: float,
        epoch_duration: float,
    ):
        """Update training metrics"""
        # Increment epoch counter
        self.training_epochs.labels(
            trainer_id=trainer_id, model_version=model_version
        ).inc()

        # Update current values
        self.training_loss.labels(
            trainer_id=trainer_id, model_version=model_version
        ).set(loss)

        self.training_val_loss.labels(
            trainer_id=trainer_id, model_version=model_version
        ).set(val_loss)

        self.training_accuracy.labels(
            trainer_id=trainer_id, model_version=model_version
        ).set(accuracy)

        self.training_val_accuracy.labels(
            trainer_id=trainer_id, model_version=model_version
        ).set(val_accuracy)

        self.training_learning_rate.labels(
            trainer_id=trainer_id, model_version=model_version
        ).set(learning_rate)

        self.training_gradient_norm.labels(
            trainer_id=trainer_id, model_version=model_version
        ).set(gradient_norm)

        # Record durations
        self.training_duration.labels(
            trainer_id=trainer_id, model_version=model_version
        ).observe(epoch_duration)

        self.training_batch_duration.labels(
            trainer_id=trainer_id, model_version=model_version
        ).observe(batch_duration)

    def update_prediction_metrics(
        self,
        symbol: str,
        model_version: str,
        latency: float,
        confidence: float,
        uncertainty: float,
    ):
        """Update prediction metrics"""
        # Increment prediction counter
        self.predictions_total.labels(symbol=symbol, model_version=model_version).inc()

        # Record metrics
        self.prediction_latency.labels(
            symbol=symbol, model_version=model_version
        ).observe(latency)

        self.prediction_confidence.labels(
            symbol=symbol, model_version=model_version
        ).observe(confidence)

        self.prediction_uncertainty.labels(
            symbol=symbol, model_version=model_version
        ).observe(uncertainty)

    def update_api_metrics(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Update API metrics"""
        # Increment request counter
        self.api_requests_total.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).inc()

        # Record duration
        self.api_request_duration.labels(method=method, endpoint=endpoint).observe(
            duration
        )

    def update_error_metrics(self, error_type: str, component: str):
        """Update error metrics"""
        self.errors_total.labels(error_type=error_type, component=component).inc()

    def update_instability_metrics(self, trainer_id: str, reason: str):
        """Update instability metrics"""
        self.instability_events_total.labels(trainer_id=trainer_id, reason=reason).inc()

    def update_checkpoint_metrics(
        self, trainer_id: str, model_version: str, action: str
    ):
        """Update checkpoint metrics"""
        if action == "save":
            self.checkpoint_saves_total.labels(
                trainer_id=trainer_id, model_version=model_version
            ).inc()
        elif action == "restore":
            self.checkpoint_restores_total.labels(
                trainer_id=trainer_id, model_version=model_version
            ).inc()

    def update_experience_replay_metrics(
        self, trainer_id: str, buffer_size: int, samples_count: int
    ):
        """Update experience replay metrics"""
        self.experience_buffer_size.labels(trainer_id=trainer_id).set(buffer_size)

        self.experience_samples_total.labels(trainer_id=trainer_id).inc(samples_count)

    def update_market_data_metrics(self, symbol: str, source: str, latency: float):
        """Update market data metrics"""
        self.market_data_updates_total.labels(symbol=symbol, source=source).inc()

        self.market_data_latency.labels(symbol=symbol, source=source).observe(latency)

    def update_backtest_metrics(
        self, symbol: str, timeframe: str, accuracy: float, sharpe_ratio: float
    ):
        """Update backtest metrics"""
        self.backtests_total.labels(symbol=symbol, timeframe=timeframe).inc()

        self.backtest_accuracy.labels(symbol=symbol, timeframe=timeframe).observe(
            accuracy
        )

        self.backtest_sharpe_ratio.labels(symbol=symbol, timeframe=timeframe).observe(
            sharpe_ratio
        )

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        return generate_latest(self.registry).decode("utf-8")

    def get_wsgi_app(self):
        """Get WSGI app for metrics endpoint"""
        return self.wsgi_app


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    return metrics_collector


# Decorator for automatic metrics collection
def track_metrics(metric_name: str, labels: Dict[str, str] = None):
    """Decorator to track function metrics"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Update metrics based on function name
                if "training" in func.__name__.lower():
                    # Training-related metrics
                    pass
                elif "prediction" in func.__name__.lower():
                    # Prediction-related metrics
                    pass
                elif "api" in func.__name__.lower():
                    # API-related metrics
                    pass

                return result
            except Exception as e:
                # Record error metrics
                metrics_collector.update_error_metrics(
                    error_type=type(e).__name__, component=func.__name__
                )
                raise

        return wrapper

    return decorator


def record_alert(alert_type: str, symbol: str, severity: str):
    """Record alert metrics"""
    logger.info(f"Alert recorded: {alert_type} for {symbol} with severity {severity}")


# Legacy metrics for backwards compatibility
REQUEST_COUNT = metrics_collector.api_requests_total
REQUEST_LATENCY = metrics_collector.api_request_duration
IN_PROGRESS_REQUESTS = Gauge("in_progress_requests", "Number of requests in progress")
DB_QUERY_COUNT = Counter("db_query_count_total", "Total database queries")
REDIS_HIT_COUNT = Counter("redis_hit_count_total", "Total Redis cache hits")
REDIS_MISS_COUNT = Counter("redis_miss_count_total", "Total Redis cache misses")
AI_PREDICTION_COUNT = metrics_collector.predictions_total
AI_TRAINING_EPOCHS = metrics_collector.training_epochs
