"""
Observability service for BOLT AI Neural Agent System
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional

from monitoring import (get_crash_dump_generator, get_logger,
                        get_metrics_collector, get_slo_monitor,
                        get_telemetry_collector)

logger = get_logger(__name__)


class ObservabilityService:
    """Centralized observability service"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.telemetry_collector = get_telemetry_collector()
        self.metrics_collector = get_metrics_collector()
        self.crash_dump_generator = get_crash_dump_generator()
        self.slo_monitor = get_slo_monitor()

        # Service state
        self.running = False
        self.start_time = None

        logger.info("Observability service initialized")

    async def start(self):
        """Start observability services"""
        if self.running:
            return

        self.running = True
        self.start_time = datetime.now()

        # Start telemetry collection
        self.telemetry_collector.start_collection(interval=1.0)

        # Start SLO monitoring
        self.slo_monitor.start_monitoring(interval=60.0)

        logger.info("Observability services started")

    async def stop(self):
        """Stop observability services"""
        if not self.running:
            return

        self.running = False

        # Stop telemetry collection
        self.telemetry_collector.stop_collection()

        # Stop SLO monitoring
        self.slo_monitor.stop_monitoring()

        logger.info("Observability services stopped")

    def record_training_start(self, trainer_id: str, config: Dict[str, Any]):
        """Record training start event"""
        self.logger.log_training_start(trainer_id, config)

        # Record telemetry event
        self.telemetry_collector.record_event(
            "training_start",
            {"trainer_id": trainer_id, "config": config},
            correlation_id=trainer_id,
        )

    def record_training_epoch(
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
        """Record training epoch event"""
        # Log training epoch
        self.logger.log_training_epoch(
            trainer_id,
            epoch,
            {
                "loss": loss,
                "val_loss": val_loss,
                "accuracy": accuracy,
                "val_accuracy": val_accuracy,
                "learning_rate": learning_rate,
                "gradient_norm": gradient_norm,
                "batch_time": batch_time,
                "epoch_time": epoch_time,
            },
        )

        # Record telemetry metrics
        self.telemetry_collector.record_training_metrics(
            trainer_id,
            epoch,
            loss,
            val_loss,
            accuracy,
            val_accuracy,
            learning_rate,
            gradient_norm,
            batch_time,
            epoch_time,
        )

        # Update Prometheus metrics
        self.metrics_collector.update_training_metrics(
            trainer_id,
            "1.0.0",
            epoch,
            loss,
            val_loss,
            accuracy,
            val_accuracy,
            learning_rate,
            gradient_norm,
            batch_time,
            epoch_time,
        )

        # Record SLO metrics
        self.slo_monitor.record_metric("prediction_latency", batch_time * 1000)

    def record_training_end(self, trainer_id: str, final_metrics: Dict[str, float]):
        """Record training end event"""
        self.logger.log_training_end(trainer_id, final_metrics)

        # Record telemetry event
        self.telemetry_collector.record_event(
            "training_end",
            {"trainer_id": trainer_id, "final_metrics": final_metrics},
            correlation_id=trainer_id,
        )

    def record_prediction(
        self,
        prediction_id: str,
        symbol: str,
        latency_ms: float,
        confidence: float,
        uncertainty: float,
        input_features: int,
        model_version: str,
    ):
        """Record prediction event"""
        # Log prediction
        self.logger.log_prediction(
            prediction_id,
            symbol,
            {
                "latency_ms": latency_ms,
                "confidence": confidence,
                "uncertainty": uncertainty,
                "input_features": input_features,
                "model_version": model_version,
            },
        )

        # Record telemetry metrics
        self.telemetry_collector.record_prediction_metrics(
            prediction_id,
            symbol,
            latency_ms,
            confidence,
            uncertainty,
            input_features,
            model_version,
        )

        # Update Prometheus metrics
        self.metrics_collector.update_prediction_metrics(
            symbol, model_version, latency_ms / 1000, confidence, uncertainty
        )

        # Record SLO metrics
        self.slo_monitor.record_metric("prediction_latency", latency_ms)

    def record_instability_event(
        self, trainer_id: str, reason: str, recovery_action: str
    ):
        """Record instability detection event"""
        self.logger.log_instability_event(trainer_id, reason, recovery_action)

        # Record telemetry event
        self.telemetry_collector.record_event(
            "instability_detected",
            {
                "trainer_id": trainer_id,
                "reason": reason,
                "recovery_action": recovery_action,
            },
            correlation_id=trainer_id,
        )

        # Update Prometheus metrics
        self.metrics_collector.update_instability_metrics(trainer_id, reason)

    def record_api_request(
        self,
        request_id: str,
        method: str,
        endpoint: str,
        status_code: int,
        duration_ms: float,
    ):
        """Record API request event"""
        self.logger.log_api_request(
            request_id, method, endpoint, status_code, duration_ms
        )

        # Update Prometheus metrics
        self.metrics_collector.update_api_metrics(
            method, endpoint, status_code, duration_ms / 1000
        )

        # Record SLO metrics
        self.slo_monitor.record_metric("api_response_time", duration_ms)

    def record_error(self, error: Exception, context: Dict[str, Any] = None):
        """Record error event"""
        self.logger.log_error(error, context)

        # Record telemetry event
        self.telemetry_collector.record_event(
            "error",
            {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context or {},
            },
        )

        # Update Prometheus metrics
        self.metrics_collector.update_error_metrics(
            type(error).__name__,
            context.get("component", "unknown") if context else "unknown",
        )

        # Generate crash dump for critical errors
        if isinstance(error, (SystemExit, KeyboardInterrupt, MemoryError)):
            self.crash_dump_generator.generate_crash_dump(
                crash_type="critical_error", exception=error, context=context
            )

    def record_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "ms",
        tags: Dict[str, str] = None,
    ):
        """Record performance metric"""
        self.logger.log_performance_metric(metric_name, value, unit, tags)

        # Record telemetry event
        self.telemetry_collector.record_event(
            "performance_metric",
            {
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "tags": tags or {},
            },
        )

        # Record SLO metrics based on metric name
        if "startup" in metric_name.lower():
            self.slo_monitor.record_metric("startup_time", value, tags)
        elif "prediction" in metric_name.lower():
            self.slo_monitor.record_metric("prediction_latency", value, tags)
        elif "ui" in metric_name.lower():
            self.slo_monitor.record_metric("ui_frame_time", value, tags)

    def record_checkpoint_event(self, trainer_id: str, model_version: str, action: str):
        """Record checkpoint event"""
        # Update Prometheus metrics
        self.metrics_collector.update_checkpoint_metrics(
            trainer_id, model_version, action
        )

        # Record telemetry event
        self.telemetry_collector.record_event(
            "checkpoint_event",
            {
                "trainer_id": trainer_id,
                "model_version": model_version,
                "action": action,
            },
            correlation_id=trainer_id,
        )

    def record_experience_replay_event(
        self, trainer_id: str, buffer_size: int, samples_count: int
    ):
        """Record experience replay event"""
        # Update Prometheus metrics
        self.metrics_collector.update_experience_replay_metrics(
            trainer_id, buffer_size, samples_count
        )

        # Record telemetry event
        self.telemetry_collector.record_event(
            "experience_replay_event",
            {
                "trainer_id": trainer_id,
                "buffer_size": buffer_size,
                "samples_count": samples_count,
            },
            correlation_id=trainer_id,
        )

    def record_market_data_event(self, symbol: str, source: str, latency: float):
        """Record market data event"""
        # Update Prometheus metrics
        self.metrics_collector.update_market_data_metrics(symbol, source, latency)

        # Record telemetry event
        self.telemetry_collector.record_event(
            "market_data_event",
            {"symbol": symbol, "source": source, "latency": latency},
        )

    def record_backtest_event(
        self, symbol: str, timeframe: str, accuracy: float, sharpe_ratio: float
    ):
        """Record backtest event"""
        # Update Prometheus metrics
        self.metrics_collector.update_backtest_metrics(
            symbol, timeframe, accuracy, sharpe_ratio
        )

        # Record telemetry event
        self.telemetry_collector.record_event(
            "backtest_event",
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "accuracy": accuracy,
                "sharpe_ratio": sharpe_ratio,
            },
        )

    def get_observability_summary(self) -> Dict[str, Any]:
        """Get comprehensive observability summary"""
        return {
            "timestamp": datetime.now().isoformat(),
            "service_status": "running" if self.running else "stopped",
            "uptime_seconds": (
                (datetime.now() - self.start_time).total_seconds()
                if self.start_time
                else 0
            ),
            "telemetry": self.telemetry_collector.get_performance_summary(),
            "slo_status": self.slo_monitor.get_slo_status(),
            "system_info": {
                "crash_dumps_count": len(
                    list(self.crash_dump_generator.output_dir.glob("*.json"))
                ),
                "output_directory": str(self.crash_dump_generator.output_dir),
            },
        }

    def export_all_data(self) -> Dict[str, str]:
        """Export all observability data"""
        exported_files = {}

        try:
            # Export telemetry data
            telemetry_files = self.telemetry_collector.export_telemetry()
            exported_files.update(telemetry_files)

            # Export SLO data
            slo_files = self.slo_monitor.export_slo_data()
            exported_files.update(slo_files)

            logger.info("All observability data exported", files=exported_files)
            return exported_files

        except Exception as e:
            logger.error("Error exporting observability data", error=str(e))
            return {}


# Global observability service instance
observability_service = ObservabilityService()


def get_observability_service() -> ObservabilityService:
    """Get global observability service instance"""
    return observability_service
