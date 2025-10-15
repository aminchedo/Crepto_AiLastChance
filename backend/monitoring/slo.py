"""
SLO monitoring and alerting for BOLT AI Neural Agent System
"""

import time
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import json
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class SLI:
    """Service Level Indicator"""

    name: str
    description: str
    unit: str
    measurement_type: str  # histogram, gauge, counter, rate
    threshold: float
    target: float
    window: str  # time window for measurement
    tags: Dict[str, str] = None


@dataclass
class SLO:
    """Service Level Objective"""

    name: str
    description: str
    target: float  # target percentage (e.g., 99.9)
    window: str  # measurement window
    tolerance: float  # tolerance threshold
    slis: List[str]  # list of SLI names


@dataclass
class SLOViolation:
    """SLO violation record"""

    timestamp: datetime
    slo_name: str
    sli_name: str
    current_value: float
    target_value: float
    violation_percentage: float
    severity: str  # warning, critical
    message: str


class SLOMonitor:
    """SLO monitoring and alerting system"""

    def __init__(self):
        self.slis: Dict[str, SLI] = {}
        self.slos: Dict[str, SLO] = {}
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.violations: deque = deque(maxlen=1000)
        self.alerts: List[Callable] = []

        # Monitoring state
        self.running = False
        self.monitor_thread = None
        self.lock = threading.Lock()

        # Load default SLIs and SLOs
        self._load_default_slis()
        self._load_default_slos()

        logger.info("SLO monitor initialized")

    def _load_default_slis(self):
        """Load default SLIs"""
        default_slis = [
            SLI(
                name="startup_time",
                description="Application startup time",
                unit="seconds",
                measurement_type="histogram",
                threshold=5.0,
                target=5.0,
                window="1h",
                tags={"component": "application"},
            ),
            SLI(
                name="prediction_latency",
                description="Prediction latency",
                unit="milliseconds",
                measurement_type="histogram",
                threshold=100.0,
                target=100.0,
                window="1h",
                tags={"component": "prediction"},
            ),
            SLI(
                name="ui_frame_time",
                description="UI frame time",
                unit="milliseconds",
                measurement_type="histogram",
                threshold=16.67,
                target=16.67,
                window="1h",
                tags={"component": "ui"},
            ),
            SLI(
                name="memory_usage",
                description="Memory usage",
                unit="GB",
                measurement_type="gauge",
                threshold=2.0,
                target=2.0,
                window="1h",
                tags={"component": "system"},
            ),
            SLI(
                name="cpu_usage",
                description="CPU usage",
                unit="percent",
                measurement_type="gauge",
                threshold=80.0,
                target=80.0,
                window="1h",
                tags={"component": "system"},
            ),
            SLI(
                name="api_response_time",
                description="API response time",
                unit="milliseconds",
                measurement_type="histogram",
                threshold=1000.0,
                target=1000.0,
                window="1h",
                tags={"component": "api"},
            ),
            SLI(
                name="error_rate",
                description="Error rate",
                unit="percent",
                measurement_type="rate",
                threshold=1.0,
                target=1.0,
                window="1h",
                tags={"component": "system"},
            ),
            SLI(
                name="availability",
                description="Service availability",
                unit="percent",
                measurement_type="rate",
                threshold=99.9,
                target=99.9,
                window="1h",
                tags={"component": "system"},
            ),
        ]

        for sli in default_slis:
            self.slis[sli.name] = sli

    def _load_default_slos(self):
        """Load default SLOs"""
        default_slos = [
            SLO(
                name="startup_time",
                description="Application startup time SLO",
                target=5.0,
                window="1h",
                tolerance=0.1,
                slis=["startup_time"],
            ),
            SLO(
                name="prediction_latency",
                description="Prediction latency SLO",
                target=100.0,
                window="1h",
                tolerance=0.05,
                slis=["prediction_latency"],
            ),
            SLO(
                name="ui_frame_time",
                description="UI frame time SLO",
                target=16.67,
                window="1h",
                tolerance=0.1,
                slis=["ui_frame_time"],
            ),
            SLO(
                name="memory_usage",
                description="Memory usage SLO",
                target=2.0,
                window="1h",
                tolerance=0.2,
                slis=["memory_usage"],
            ),
            SLO(
                name="cpu_usage",
                description="CPU usage SLO",
                target=80.0,
                window="1h",
                tolerance=0.1,
                slis=["cpu_usage"],
            ),
            SLO(
                name="api_response_time",
                description="API response time SLO",
                target=1000.0,
                window="1h",
                tolerance=0.05,
                slis=["api_response_time"],
            ),
            SLO(
                name="error_rate",
                description="Error rate SLO",
                target=1.0,
                window="1h",
                tolerance=0.1,
                slis=["error_rate"],
            ),
            SLO(
                name="availability",
                description="Service availability SLO",
                target=99.9,
                window="1h",
                tolerance=0.001,
                slis=["availability"],
            ),
        ]

        for slo in default_slos:
            self.slos[slo.name] = slo

    def start_monitoring(self, interval: float = 60.0):
        """Start SLO monitoring"""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, args=(interval,), daemon=True
        )
        self.monitor_thread.start()

        logger.info("SLO monitoring started", interval=interval)

    def stop_monitoring(self):
        """Stop SLO monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)

        logger.info("SLO monitoring stopped")

    def _monitoring_loop(self, interval: float):
        """Main monitoring loop"""
        while self.running:
            try:
                self._evaluate_slos()
                time.sleep(interval)
            except Exception as e:
                logger.error("Error in SLO monitoring loop", error=str(e))
                time.sleep(interval)

    def record_metric(self, sli_name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric value for an SLI"""
        if sli_name not in self.slis:
            logger.warning(f"Unknown SLI: {sli_name}")
            return

        metric_data = {"timestamp": datetime.now(), "value": value, "tags": tags or {}}

        with self.lock:
            self.metrics[sli_name].append(metric_data)

        logger.debug(f"Recorded metric for {sli_name}", value=value, tags=tags)

    def _evaluate_slos(self):
        """Evaluate all SLOs"""
        for slo_name, slo in self.slos.items():
            try:
                self._evaluate_slo(slo)
            except Exception as e:
                logger.error(f"Error evaluating SLO {slo_name}", error=str(e))

    def _evaluate_slo(self, slo: SLO):
        """Evaluate a single SLO"""
        for sli_name in slo.slis:
            if sli_name not in self.slis:
                continue

            sli = self.slis[sli_name]
            current_value = self._get_current_sli_value(sli_name)

            if current_value is None:
                continue

            # Check if SLO is violated
            violation_percentage = self._calculate_violation_percentage(
                current_value, slo.target, sli.measurement_type
            )

            if violation_percentage > slo.tolerance:
                # Determine severity
                severity = (
                    "critical"
                    if violation_percentage > slo.tolerance * 2
                    else "warning"
                )

                # Create violation record
                violation = SLOViolation(
                    timestamp=datetime.now(),
                    slo_name=slo.name,
                    sli_name=sli_name,
                    current_value=current_value,
                    target_value=slo.target,
                    violation_percentage=violation_percentage,
                    severity=severity,
                    message=f"SLO violation: {slo.name} - {sli_name} = {current_value:.2f} (target: {slo.target:.2f})",
                )

                # Record violation
                with self.lock:
                    self.violations.append(violation)

                # Send alerts
                self._send_alerts(violation)

                logger.warning(
                    "SLO violation detected",
                    slo_name=slo.name,
                    sli_name=sli_name,
                    current_value=current_value,
                    target_value=slo.target,
                    violation_percentage=violation_percentage,
                    severity=severity,
                )

    def _get_current_sli_value(self, sli_name: str) -> Optional[float]:
        """Get current value for an SLI"""
        if sli_name not in self.metrics:
            return None

        with self.lock:
            metrics = list(self.metrics[sli_name])

        if not metrics:
            return None

        sli = self.slis[sli_name]

        # Calculate value based on measurement type
        if sli.measurement_type == "histogram":
            # Use 95th percentile
            values = [m["value"] for m in metrics]
            values.sort()
            percentile_index = int(len(values) * 0.95)
            return (
                values[percentile_index]
                if percentile_index < len(values)
                else values[-1]
            )

        elif sli.measurement_type == "gauge":
            # Use current value
            return metrics[-1]["value"]

        elif sli.measurement_type == "counter":
            # Use rate over time window
            return self._calculate_rate(metrics)

        elif sli.measurement_type == "rate":
            # Use rate over time window
            return self._calculate_rate(metrics)

        return None

    def _calculate_rate(self, metrics: List[Dict]) -> float:
        """Calculate rate over time window"""
        if len(metrics) < 2:
            return 0.0

        # Calculate rate over last hour
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)

        recent_metrics = [m for m in metrics if m["timestamp"] > one_hour_ago]

        if len(recent_metrics) < 2:
            return 0.0

        time_diff = (
            recent_metrics[-1]["timestamp"] - recent_metrics[0]["timestamp"]
        ).total_seconds()
        value_diff = recent_metrics[-1]["value"] - recent_metrics[0]["value"]

        return value_diff / time_diff if time_diff > 0 else 0.0

    def _calculate_violation_percentage(
        self, current_value: float, target: float, measurement_type: str
    ) -> float:
        """Calculate violation percentage"""
        if measurement_type in ["histogram", "gauge"]:
            # For histograms and gauges, check if value exceeds threshold
            if current_value <= target:
                return 0.0
            return (current_value - target) / target

        elif measurement_type in ["counter", "rate"]:
            # For counters and rates, check if value is below threshold (for availability)
            if current_value >= target:
                return 0.0
            return (target - current_value) / target

        return 0.0

    def _send_alerts(self, violation: SLOViolation):
        """Send alerts for SLO violations"""
        # Import here to avoid circular imports
        from .alerting import get_alert_manager

        alert_manager = get_alert_manager()

        # Send SLO violation alert
        asyncio.create_task(
            alert_manager.send_slo_violation_alert(
                violation.slo_name,
                violation.sli_name,
                violation.current_value,
                violation.target_value,
                violation.violation_percentage,
                violation.severity,
            )
        )

        # Also call custom alert handlers
        for alert_func in self.alerts:
            try:
                alert_func(violation)
            except Exception as e:
                logger.error("Error sending alert", error=str(e))

    def add_alert_handler(self, alert_func: Callable[[SLOViolation], None]):
        """Add alert handler"""
        self.alerts.append(alert_func)

    def get_slo_status(self) -> Dict[str, Any]:
        """Get current SLO status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "slos": {},
            "violations": {"total": len(self.violations), "recent": []},
        }

        # Get recent violations
        with self.lock:
            recent_violations = list(self.violations)[-10:]  # Last 10 violations

        status["violations"]["recent"] = [asdict(v) for v in recent_violations]

        # Evaluate each SLO
        for slo_name, slo in self.slos.items():
            slo_status = {
                "name": slo.name,
                "description": slo.description,
                "target": slo.target,
                "window": slo.window,
                "tolerance": slo.tolerance,
                "status": "healthy",
                "slis": {},
            }

            for sli_name in slo.slis:
                if sli_name not in self.slis:
                    continue

                sli = self.slis[sli_name]
                current_value = self._get_current_sli_value(sli_name)

                sli_status = {
                    "name": sli.name,
                    "description": sli.description,
                    "unit": sli.unit,
                    "current_value": current_value,
                    "target": sli.target,
                    "status": "healthy",
                }

                if current_value is not None:
                    violation_percentage = self._calculate_violation_percentage(
                        current_value, slo.target, sli.measurement_type
                    )

                    if violation_percentage > slo.tolerance:
                        sli_status["status"] = "violated"
                        slo_status["status"] = "violated"
                        sli_status["violation_percentage"] = violation_percentage

                slo_status["slis"][sli_name] = sli_status

            status["slos"][slo_name] = slo_status

        return status

    def export_slo_data(self, output_dir: Path = None) -> Dict[str, str]:
        """Export SLO data to files"""
        if output_dir is None:
            output_dir = Path("slo_exports")

        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        exported_files = {}

        # Export SLO status
        status_file = output_dir / f"slo_status_{timestamp}.json"
        with open(status_file, "w") as f:
            json.dump(self.get_slo_status(), f, indent=2, default=str)
        exported_files["status"] = str(status_file)

        # Export violations
        violations_file = output_dir / f"slo_violations_{timestamp}.json"
        with self.lock:
            violations_data = [asdict(v) for v in self.violations]

        with open(violations_file, "w") as f:
            json.dump(violations_data, f, indent=2, default=str)
        exported_files["violations"] = str(violations_file)

        # Export metrics
        metrics_file = output_dir / f"slo_metrics_{timestamp}.json"
        with self.lock:
            metrics_data = {}
            for sli_name, metrics in self.metrics.items():
                metrics_data[sli_name] = [asdict(m) for m in metrics]

        with open(metrics_file, "w") as f:
            json.dump(metrics_data, f, indent=2, default=str)
        exported_files["metrics"] = str(metrics_file)

        logger.info("SLO data exported", files=exported_files)
        return exported_files


# Global SLO monitor instance
slo_monitor = SLOMonitor()


def get_slo_monitor() -> SLOMonitor:
    """Get global SLO monitor instance"""
    return slo_monitor


# Decorator for automatic SLO monitoring
def monitor_slo(sli_name: str, tags: Dict[str, str] = None):
    """Decorator to monitor function performance against SLOs"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Record metric
                if sli_name == "prediction_latency":
                    slo_monitor.record_metric(sli_name, duration * 1000, tags)
                elif sli_name == "api_response_time":
                    slo_monitor.record_metric(sli_name, duration * 1000, tags)
                elif sli_name == "startup_time":
                    slo_monitor.record_metric(sli_name, duration, tags)

                return result
            except Exception as e:
                # Record error
                slo_monitor.record_metric("error_rate", 1.0, tags)
                raise

        return wrapper

    return decorator
