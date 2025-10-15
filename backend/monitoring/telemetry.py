"""
Telemetry system for BOLT AI Neural Agent System
"""

import json
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class TelemetryEvent:
    """Telemetry event data structure"""

    timestamp: datetime
    event_type: str
    data: Dict[str, Any]
    correlation_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""

    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    memory_available: float
    disk_usage: float
    network_io: Dict[str, int]
    gpu_usage: Optional[float] = None
    gpu_memory: Optional[float] = None


@dataclass
class TrainingMetrics:
    """Training metrics data structure"""

    timestamp: datetime
    trainer_id: str
    epoch: int
    loss: float
    val_loss: float
    accuracy: float
    val_accuracy: float
    learning_rate: float
    gradient_norm: float
    batch_time: float
    epoch_time: float


@dataclass
class PredictionMetrics:
    """Prediction metrics data structure"""

    timestamp: datetime
    prediction_id: str
    symbol: str
    latency_ms: float
    confidence: float
    uncertainty: float
    input_features: int
    model_version: str


class TelemetryCollector:
    """Telemetry data collector"""

    def __init__(self, buffer_size: int = 10000):
        self.buffer_size = buffer_size
        self.events = deque(maxlen=buffer_size)
        self.performance_metrics = deque(maxlen=1000)
        self.training_metrics = deque(maxlen=1000)
        self.prediction_metrics = deque(maxlen=1000)

        # Metrics aggregation
        self.metrics_aggregation = defaultdict(list)
        self.aggregation_window = timedelta(minutes=5)

        # Threading
        self.lock = threading.Lock()
        self.running = False
        self.collection_thread = None

        # Performance monitoring
        self.start_time = datetime.now()
        self.session_id = self._generate_session_id()

        logger.info("Telemetry collector initialized", session_id=self.session_id)

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{int(time.time())}_{id(self)}"

    def start_collection(self, interval: float = 1.0):
        """Start telemetry collection"""
        if self.running:
            return

        self.running = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop, args=(interval,), daemon=True
        )
        self.collection_thread.start()

        logger.info("Telemetry collection started", interval=interval)

    def stop_collection(self):
        """Stop telemetry collection"""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5.0)

        logger.info("Telemetry collection stopped")

    def _collection_loop(self, interval: float):
        """Main collection loop"""
        while self.running:
            try:
                self._collect_performance_metrics()
                self._aggregate_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.error("Error in telemetry collection", error=str(e))
                time.sleep(interval)

    def _collect_performance_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=0.1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            memory_available = memory.available / (1024**3)  # GB

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_usage = (disk.used / disk.total) * 100

            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            }

            # GPU usage (if available)
            gpu_usage = None
            gpu_memory = None
            try:
                import GPUtil

                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    gpu_usage = gpu.load * 100
                    gpu_memory = gpu.memoryUsed / gpu.memoryTotal * 100
            except ImportError:
                pass

            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                memory_available=memory_available,
                disk_usage=disk_usage,
                network_io=network_io,
                gpu_usage=gpu_usage,
                gpu_memory=gpu_memory,
            )

            with self.lock:
                self.performance_metrics.append(metrics)

        except Exception as e:
            logger.error("Error collecting performance metrics", error=str(e))

    def _aggregate_metrics(self):
        """Aggregate metrics over time window"""
        now = datetime.now()
        cutoff_time = now - self.aggregation_window

        # Clean old metrics
        with self.lock:
            # Performance metrics
            while (
                self.performance_metrics
                and self.performance_metrics[0].timestamp < cutoff_time
            ):
                self.performance_metrics.popleft()

            # Training metrics
            while (
                self.training_metrics
                and self.training_metrics[0].timestamp < cutoff_time
            ):
                self.training_metrics.popleft()

            # Prediction metrics
            while (
                self.prediction_metrics
                and self.prediction_metrics[0].timestamp < cutoff_time
            ):
                self.prediction_metrics.popleft()

    def record_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ):
        """Record a telemetry event"""
        event = TelemetryEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            data=data,
            correlation_id=correlation_id,
            session_id=self.session_id,
        )

        with self.lock:
            self.events.append(event)

        logger.debug("Telemetry event recorded", event_type=event_type)

    def record_training_metrics(
        self,
        trainer_id: str,
        epoch: int,
        loss: float,
        val_loss: float,
        accuracy: float,
        val_accuracy: float,
        learning_rate: float,
        gradient_norm: float,
        batch_time: float,
        epoch_time: float,
    ):
        """Record training metrics"""
        metrics = TrainingMetrics(
            timestamp=datetime.now(),
            trainer_id=trainer_id,
            epoch=epoch,
            loss=loss,
            val_loss=val_loss,
            accuracy=accuracy,
            val_accuracy=val_accuracy,
            learning_rate=learning_rate,
            gradient_norm=gradient_norm,
            batch_time=batch_time,
            epoch_time=epoch_time,
        )

        with self.lock:
            self.training_metrics.append(metrics)

        # Also record as event
        self.record_event(
            "training_metrics", asdict(metrics), correlation_id=trainer_id
        )

    def record_prediction_metrics(
        self,
        prediction_id: str,
        symbol: str,
        latency_ms: float,
        confidence: float,
        uncertainty: float,
        input_features: int,
        model_version: str,
    ):
        """Record prediction metrics"""
        metrics = PredictionMetrics(
            timestamp=datetime.now(),
            prediction_id=prediction_id,
            symbol=symbol,
            latency_ms=latency_ms,
            confidence=confidence,
            uncertainty=uncertainty,
            input_features=input_features,
            model_version=model_version,
        )

        with self.lock:
            self.prediction_metrics.append(metrics)

        # Also record as event
        self.record_event(
            "prediction_metrics", asdict(metrics), correlation_id=prediction_id
        )

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        with self.lock:
            if not self.performance_metrics:
                return {}

            metrics = list(self.performance_metrics)

        # Calculate aggregates
        cpu_values = [m.cpu_usage for m in metrics]
        memory_values = [m.memory_usage for m in metrics]
        disk_values = [m.disk_usage for m in metrics]

        summary = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "metrics_count": len(metrics),
            "cpu": {
                "current": cpu_values[-1] if cpu_values else 0,
                "avg": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "max": max(cpu_values) if cpu_values else 0,
                "min": min(cpu_values) if cpu_values else 0,
            },
            "memory": {
                "current": memory_values[-1] if memory_values else 0,
                "avg": sum(memory_values) / len(memory_values) if memory_values else 0,
                "max": max(memory_values) if memory_values else 0,
                "min": min(memory_values) if memory_values else 0,
            },
            "disk": {
                "current": disk_values[-1] if disk_values else 0,
                "avg": sum(disk_values) / len(disk_values) if disk_values else 0,
                "max": max(disk_values) if disk_values else 0,
                "min": min(disk_values) if disk_values else 0,
            },
        }

        # Add GPU metrics if available
        gpu_metrics = [m for m in metrics if m.gpu_usage is not None]
        if gpu_metrics:
            gpu_values = [m.gpu_usage for m in gpu_metrics]
            gpu_memory_values = [m.gpu_memory for m in gpu_metrics]

            summary["gpu"] = {
                "usage": {
                    "current": gpu_values[-1] if gpu_values else 0,
                    "avg": sum(gpu_values) / len(gpu_values) if gpu_values else 0,
                    "max": max(gpu_values) if gpu_values else 0,
                    "min": min(gpu_values) if gpu_values else 0,
                },
                "memory": {
                    "current": gpu_memory_values[-1] if gpu_memory_values else 0,
                    "avg": (
                        sum(gpu_memory_values) / len(gpu_memory_values)
                        if gpu_memory_values
                        else 0
                    ),
                    "max": max(gpu_memory_values) if gpu_memory_values else 0,
                    "min": min(gpu_memory_values) if gpu_memory_values else 0,
                },
            }

        return summary

    def get_training_summary(self) -> Dict[str, Any]:
        """Get training metrics summary"""
        with self.lock:
            if not self.training_metrics:
                return {}

            metrics = list(self.training_metrics)

        # Group by trainer
        trainers = defaultdict(list)
        for metric in metrics:
            trainers[metric.trainer_id].append(metric)

        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_trainers": len(trainers),
            "total_epochs": len(metrics),
            "trainers": {},
        }

        for trainer_id, trainer_metrics in trainers.items():
            if not trainer_metrics:
                continue

            # Calculate aggregates
            losses = [m.loss for m in trainer_metrics]
            val_losses = [m.val_loss for m in trainer_metrics]
            accuracies = [m.accuracy for m in trainer_metrics]
            val_accuracies = [m.val_accuracy for m in trainer_metrics]
            learning_rates = [m.learning_rate for m in trainer_metrics]
            gradient_norms = [m.gradient_norm for m in trainer_metrics]
            batch_times = [m.batch_time for m in trainer_metrics]
            epoch_times = [m.epoch_time for m in trainer_metrics]

            summary["trainers"][trainer_id] = {
                "epochs": len(trainer_metrics),
                "latest_epoch": trainer_metrics[-1].epoch,
                "loss": {
                    "current": losses[-1] if losses else 0,
                    "avg": sum(losses) / len(losses) if losses else 0,
                    "min": min(losses) if losses else 0,
                    "max": max(losses) if losses else 0,
                },
                "val_loss": {
                    "current": val_losses[-1] if val_losses else 0,
                    "avg": sum(val_losses) / len(val_losses) if val_losses else 0,
                    "min": min(val_losses) if val_losses else 0,
                    "max": max(val_losses) if val_losses else 0,
                },
                "accuracy": {
                    "current": accuracies[-1] if accuracies else 0,
                    "avg": sum(accuracies) / len(accuracies) if accuracies else 0,
                    "min": min(accuracies) if accuracies else 0,
                    "max": max(accuracies) if accuracies else 0,
                },
                "val_accuracy": {
                    "current": val_accuracies[-1] if val_accuracies else 0,
                    "avg": (
                        sum(val_accuracies) / len(val_accuracies)
                        if val_accuracies
                        else 0
                    ),
                    "min": min(val_accuracies) if val_accuracies else 0,
                    "max": max(val_accuracies) if val_accuracies else 0,
                },
                "learning_rate": {
                    "current": learning_rates[-1] if learning_rates else 0,
                    "avg": (
                        sum(learning_rates) / len(learning_rates)
                        if learning_rates
                        else 0
                    ),
                    "min": min(learning_rates) if learning_rates else 0,
                    "max": max(learning_rates) if learning_rates else 0,
                },
                "gradient_norm": {
                    "current": gradient_norms[-1] if gradient_norms else 0,
                    "avg": (
                        sum(gradient_norms) / len(gradient_norms)
                        if gradient_norms
                        else 0
                    ),
                    "min": min(gradient_norms) if gradient_norms else 0,
                    "max": max(gradient_norms) if gradient_norms else 0,
                },
                "timing": {
                    "avg_batch_time": (
                        sum(batch_times) / len(batch_times) if batch_times else 0
                    ),
                    "avg_epoch_time": (
                        sum(epoch_times) / len(epoch_times) if epoch_times else 0
                    ),
                    "total_training_time": sum(epoch_times) if epoch_times else 0,
                },
            }

        return summary

    def get_prediction_summary(self) -> Dict[str, Any]:
        """Get prediction metrics summary"""
        with self.lock:
            if not self.prediction_metrics:
                return {}

            metrics = list(self.prediction_metrics)

        # Group by symbol
        symbols = defaultdict(list)
        for metric in metrics:
            symbols[metric.symbol].append(metric)

        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_predictions": len(metrics),
            "total_symbols": len(symbols),
            "symbols": {},
        }

        for symbol, symbol_metrics in symbols.items():
            if not symbol_metrics:
                continue

            # Calculate aggregates
            latencies = [m.latency_ms for m in symbol_metrics]
            confidences = [m.confidence for m in symbol_metrics]
            uncertainties = [m.uncertainty for m in symbol_metrics]

            summary["symbols"][symbol] = {
                "predictions": len(symbol_metrics),
                "latency_ms": {
                    "current": latencies[-1] if latencies else 0,
                    "avg": sum(latencies) / len(latencies) if latencies else 0,
                    "min": min(latencies) if latencies else 0,
                    "max": max(latencies) if latencies else 0,
                    "p95": (
                        sorted(latencies)[int(len(latencies) * 0.95)]
                        if latencies
                        else 0
                    ),
                },
                "confidence": {
                    "current": confidences[-1] if confidences else 0,
                    "avg": sum(confidences) / len(confidences) if confidences else 0,
                    "min": min(confidences) if confidences else 0,
                    "max": max(confidences) if confidences else 0,
                },
                "uncertainty": {
                    "current": uncertainties[-1] if uncertainties else 0,
                    "avg": (
                        sum(uncertainties) / len(uncertainties) if uncertainties else 0
                    ),
                    "min": min(uncertainties) if uncertainties else 0,
                    "max": max(uncertainties) if uncertainties else 0,
                },
            }

        return summary

    def export_telemetry(self, output_dir: Path = None) -> Dict[str, str]:
        """Export telemetry data to files"""
        if output_dir is None:
            output_dir = Path("telemetry_exports")

        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        exported_files = {}

        # Export events
        with self.lock:
            events_data = [asdict(event) for event in self.events]

        events_file = output_dir / f"events_{timestamp}.json"
        with open(events_file, "w") as f:
            json.dump(events_data, f, indent=2, default=str)
        exported_files["events"] = str(events_file)

        # Export performance metrics
        with self.lock:
            performance_data = [asdict(metric) for metric in self.performance_metrics]

        performance_file = output_dir / f"performance_{timestamp}.json"
        with open(performance_file, "w") as f:
            json.dump(performance_data, f, indent=2, default=str)
        exported_files["performance"] = str(performance_file)

        # Export training metrics
        with self.lock:
            training_data = [asdict(metric) for metric in self.training_metrics]

        training_file = output_dir / f"training_{timestamp}.json"
        with open(training_file, "w") as f:
            json.dump(training_data, f, indent=2, default=str)
        exported_files["training"] = str(training_file)

        # Export prediction metrics
        with self.lock:
            prediction_data = [asdict(metric) for metric in self.prediction_metrics]

        prediction_file = output_dir / f"prediction_{timestamp}.json"
        with open(prediction_file, "w") as f:
            json.dump(prediction_data, f, indent=2, default=str)
        exported_files["prediction"] = str(prediction_file)

        # Export summaries
        summaries = {
            "performance": self.get_performance_summary(),
            "training": self.get_training_summary(),
            "prediction": self.get_prediction_summary(),
        }

        summaries_file = output_dir / f"summaries_{timestamp}.json"
        with open(summaries_file, "w") as f:
            json.dump(summaries, f, indent=2, default=str)
        exported_files["summaries"] = str(summaries_file)

        logger.info("Telemetry data exported", files=exported_files)
        return exported_files


# Global telemetry collector instance
telemetry_collector = TelemetryCollector()


def get_telemetry_collector() -> TelemetryCollector:
    """Get global telemetry collector instance"""
    return telemetry_collector


# Decorator for automatic telemetry collection
def track_performance(func):
    """Decorator to track function performance"""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        correlation_id = f"{func.__name__}_{int(time.time())}"

        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000

            telemetry_collector.record_event(
                "function_performance",
                {
                    "function": func.__name__,
                    "duration_ms": duration_ms,
                    "success": True,
                },
                correlation_id=correlation_id,
            )

            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            telemetry_collector.record_event(
                "function_performance",
                {
                    "function": func.__name__,
                    "duration_ms": duration_ms,
                    "success": False,
                    "error": str(e),
                },
                correlation_id=correlation_id,
            )

            raise

    return wrapper
