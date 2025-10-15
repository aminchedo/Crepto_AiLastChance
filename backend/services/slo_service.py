"""
SLO service for BOLT AI Neural Agent System
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

import structlog
from monitoring.slo import SLOMonitor, SLOViolation

from monitoring import get_alert_manager, get_slo_monitor

logger = structlog.get_logger(__name__)


class SLOService:
    """Centralized SLO service"""

    def __init__(self):
        self.slo_monitor = get_slo_monitor()
        self.alert_manager = get_alert_manager()
        self.running = False

        # SLO configuration
        self.slo_configs = {
            "startup_time": {
                "target": 5.0,
                "tolerance": 0.1,
                "severity_thresholds": {"warning": 0.8, "critical": 0.9},
            },
            "prediction_latency": {
                "target": 100.0,
                "tolerance": 0.05,
                "severity_thresholds": {"warning": 0.8, "critical": 0.9},
            },
            "ui_frame_time": {
                "target": 16.67,
                "tolerance": 0.1,
                "severity_thresholds": {"warning": 0.8, "critical": 0.9},
            },
            "memory_usage": {
                "target": 2.0,
                "tolerance": 0.2,
                "severity_thresholds": {"warning": 0.8, "critical": 0.9},
            },
            "cpu_usage": {
                "target": 80.0,
                "tolerance": 0.1,
                "severity_thresholds": {"warning": 0.8, "critical": 0.9},
            },
            "api_response_time": {
                "target": 1000.0,
                "tolerance": 0.05,
                "severity_thresholds": {"warning": 0.8, "critical": 0.9},
            },
            "error_rate": {
                "target": 1.0,
                "tolerance": 0.1,
                "severity_thresholds": {"warning": 0.8, "critical": 0.9},
            },
            "availability": {
                "target": 99.9,
                "tolerance": 0.001,
                "severity_thresholds": {"warning": 0.9, "critical": 0.95},
            },
        }

        logger.info("SLO service initialized")

    async def start(self):
        """Start SLO service"""
        if self.running:
            return

        self.running = True

        # Start SLO monitoring
        self.slo_monitor.start_monitoring(interval=60.0)

        # Setup alert channels
        await self._setup_alert_channels()

        logger.info("SLO service started")

    async def stop(self):
        """Stop SLO service"""
        if not self.running:
            return

        self.running = False

        # Stop SLO monitoring
        self.slo_monitor.stop_monitoring()

        logger.info("SLO service stopped")

    async def _setup_alert_channels(self):
        """Setup alert channels"""
        try:
            # This would typically load from configuration
            # For now, we'll set up basic channels

            # Slack channel (if configured)
            slack_webhook = None  # Load from environment/config
            if slack_webhook:
                from monitoring.alerting import AlertChannel

                slack_channel = AlertChannel(
                    name="slack_main",
                    enabled=True,
                    config={"webhook_url": slack_webhook, "channel": "#alerts"},
                )
                self.alert_manager.add_channel("slack_main", slack_channel)

            # Email channel (if configured)
            email_config = None  # Load from environment/config
            if email_config:
                from monitoring.alerting import AlertChannel

                email_channel = AlertChannel(
                    name="email_main", enabled=True, config=email_config
                )
                self.alert_manager.add_channel("email_main", email_channel)

            # Set up rate limits
            self.alert_manager.set_rate_limit(
                "slo_violation", max_count=5, window_seconds=300
            )
            self.alert_manager.set_rate_limit(
                "training_alert", max_count=10, window_seconds=600
            )
            self.alert_manager.set_rate_limit(
                "system_alert", max_count=20, window_seconds=600
            )

            logger.info("Alert channels configured")

        except Exception as e:
            logger.error("Error setting up alert channels", error=str(e))

    def record_metric(self, sli_name: str, value: float, tags: Dict[str, str] = None):
        """Record SLO metric"""
        self.slo_monitor.record_metric(sli_name, value, tags)

    def get_slo_status(self) -> Dict[str, Any]:
        """Get current SLO status"""
        return self.slo_monitor.get_slo_status()

    def get_slo_compliance(self) -> Dict[str, Any]:
        """Get SLO compliance summary"""
        status = self.get_slo_status()

        compliance_summary = {
            "timestamp": datetime.now().isoformat(),
            "overall_compliance": "healthy",
            "slo_summary": {},
            "violations": {
                "total": len(status.get("violations", {}).get("recent", [])),
                "critical": 0,
                "warning": 0,
            },
        }

        # Analyze SLO status
        critical_violations = 0
        warning_violations = 0

        for slo_name, slo_data in status.get("slos", {}).items():
            slo_compliance = {
                "status": slo_data.get("status", "unknown"),
                "target": slo_data.get("target", 0),
                "slis": {},
            }

            for sli_name, sli_data in slo_data.get("slis", {}).items():
                sli_status = sli_data.get("status", "unknown")
                sli_compliance = {
                    "status": sli_status,
                    "current_value": sli_data.get("current_value"),
                    "target": sli_data.get("target"),
                    "violation_percentage": sli_data.get("violation_percentage", 0),
                }

                slo_compliance["slis"][sli_name] = sli_compliance

                if sli_status == "violated":
                    violation_percentage = sli_data.get("violation_percentage", 0)
                    if violation_percentage > 0.9:  # Critical threshold
                        critical_violations += 1
                    else:
                        warning_violations += 1

            compliance_summary["slo_summary"][slo_name] = slo_compliance

        # Update overall compliance
        if critical_violations > 0:
            compliance_summary["overall_compliance"] = "critical"
        elif warning_violations > 0:
            compliance_summary["overall_compliance"] = "degraded"

        compliance_summary["violations"]["critical"] = critical_violations
        compliance_summary["violations"]["warning"] = warning_violations

        return compliance_summary

    def check_release_gate(self) -> Dict[str, Any]:
        """Check if release gate conditions are met"""
        compliance = self.get_slo_compliance()

        gate_status = {
            "timestamp": datetime.now().isoformat(),
            "gate_open": True,
            "blocking_issues": [],
            "compliance_status": compliance["overall_compliance"],
        }

        # Check for blocking issues
        if compliance["overall_compliance"] == "critical":
            gate_status["gate_open"] = False
            gate_status["blocking_issues"].append("Critical SLO violations detected")

        if compliance["violations"]["critical"] > 0:
            gate_status["gate_open"] = False
            gate_status["blocking_issues"].append(
                f"{compliance['violations']['critical']} critical violations"
            )

        # Check specific SLOs
        for slo_name, slo_data in compliance["slo_summary"].items():
            if slo_data["status"] == "violated":
                for sli_name, sli_data in slo_data["slis"].items():
                    if sli_data["status"] == "violated":
                        violation_percentage = sli_data.get("violation_percentage", 0)
                        if violation_percentage > 0.9:  # Critical threshold
                            gate_status["blocking_issues"].append(
                                f"Critical violation: {slo_name}.{sli_name} ({violation_percentage:.1%})"
                            )

        return gate_status

    async def send_training_alert(
        self,
        alert_type: str,
        trainer_id: str,
        message: str,
        severity: str = "warning",
        metadata: Dict[str, Any] = None,
    ):
        """Send training-related alert"""
        return await self.alert_manager.send_training_alert(
            alert_type, trainer_id, message, severity, metadata
        )

    async def send_system_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "warning",
        metadata: Dict[str, Any] = None,
    ):
        """Send system-related alert"""
        return await self.alert_manager.send_system_alert(
            alert_type, message, severity, metadata
        )

    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        return self.alert_manager.get_alert_stats()

    def get_alert_history(self, limit: int = 100) -> list:
        """Get alert history"""
        return self.alert_manager.get_alert_history(limit)

    def export_slo_data(self) -> Dict[str, str]:
        """Export SLO data"""
        return self.slo_monitor.export_slo_data()

    def configure_slo(self, slo_name: str, config: Dict[str, Any]):
        """Configure SLO parameters"""
        if slo_name in self.slo_configs:
            self.slo_configs[slo_name].update(config)
            logger.info("SLO configuration updated", slo_name=slo_name, config=config)
        else:
            logger.warning("Unknown SLO name", slo_name=slo_name)

    def get_slo_config(self, slo_name: str) -> Optional[Dict[str, Any]]:
        """Get SLO configuration"""
        return self.slo_configs.get(slo_name)

    def list_slos(self) -> list:
        """List all configured SLOs"""
        return list(self.slo_configs.keys())

    def get_slo_metrics(self) -> Dict[str, Any]:
        """Get SLO metrics summary"""
        status = self.get_slo_status()

        metrics_summary = {
            "timestamp": datetime.now().isoformat(),
            "active_slos": len(status.get("slos", {})),
            "total_violations": status.get("violations", {}).get("total", 0),
            "recent_violations": len(status.get("violations", {}).get("recent", [])),
            "slo_details": {},
        }

        for slo_name, slo_data in status.get("slos", {}).items():
            slo_metrics = {
                "status": slo_data.get("status"),
                "target": slo_data.get("target"),
                "tolerance": slo_data.get("tolerance"),
                "slis": {},
            }

            for sli_name, sli_data in slo_data.get("slis", {}).items():
                sli_metrics = {
                    "status": sli_data.get("status"),
                    "current_value": sli_data.get("current_value"),
                    "target": sli_data.get("target"),
                    "violation_percentage": sli_data.get("violation_percentage", 0),
                }
                slo_metrics["slis"][sli_name] = sli_metrics

            metrics_summary["slo_details"][slo_name] = slo_metrics

        return metrics_summary


# Global SLO service instance
slo_service = SLOService()


def get_slo_service() -> SLOService:
    """Get global SLO service instance"""
    return slo_service
