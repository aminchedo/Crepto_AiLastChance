"""
Alerting system for BOLT AI Neural Agent System
"""

import asyncio
import json
import smtplib
from dataclasses import asdict, dataclass
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Callable, Dict, List, Optional

import requests
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class Alert:
    """Alert data structure"""

    timestamp: datetime
    alert_type: str
    severity: str  # info, warning, critical
    title: str
    message: str
    source: str
    metadata: Dict[str, Any] = None
    correlation_id: Optional[str] = None


@dataclass
class AlertChannel:
    """Alert channel configuration"""

    name: str
    enabled: bool
    config: Dict[str, Any]
    filters: Dict[str, Any] = None


class SlackAlertChannel:
    """Slack alert channel"""

    def __init__(self, webhook_url: str, channel: str = "#alerts"):
        self.webhook_url = webhook_url
        self.channel = channel

    async def send_alert(self, alert: Alert) -> bool:
        """Send alert to Slack"""
        try:
            # Determine color based on severity
            color_map = {
                "info": "#36a64f",  # Green
                "warning": "#ff9500",  # Orange
                "critical": "#ff0000",  # Red
            }
            color = color_map.get(alert.severity, "#36a64f")

            # Create Slack message
            slack_message = {
                "channel": self.channel,
                "username": "BOLT AI Alert Bot",
                "icon_emoji": ":robot_face:",
                "attachments": [
                    {
                        "color": color,
                        "title": alert.title,
                        "text": alert.message,
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert.severity.upper(),
                                "short": True,
                            },
                            {"title": "Source", "value": alert.source, "short": True},
                            {
                                "title": "Timestamp",
                                "value": alert.timestamp.strftime(
                                    "%Y-%m-%d %H:%M:%S UTC"
                                ),
                                "short": True,
                            },
                        ],
                        "footer": "BOLT AI Neural Agent System",
                        "ts": int(alert.timestamp.timestamp()),
                    }
                ],
            }

            # Add metadata if available
            if alert.metadata:
                metadata_text = "\n".join(
                    [f"{k}: {v}" for k, v in alert.metadata.items()]
                )
                slack_message["attachments"][0]["fields"].append(
                    {"title": "Details", "value": metadata_text, "short": False}
                )

            # Send to Slack
            response = requests.post(self.webhook_url, json=slack_message, timeout=10)

            if response.status_code == 200:
                logger.info(
                    "Alert sent to Slack",
                    alert_type=alert.alert_type,
                    severity=alert.severity,
                )
                return True
            else:
                logger.error(
                    "Failed to send alert to Slack",
                    status_code=response.status_code,
                    response=response.text,
                )
                return False

        except Exception as e:
            logger.error("Error sending alert to Slack", error=str(e))
            return False


class EmailAlertChannel:
    """Email alert channel"""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
        to_emails: List[str],
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails

    async def send_alert(self, alert: Alert) -> bool:
        """Send alert via email"""
        try:
            # Create email message
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)
            msg["Subject"] = f"[{alert.severity.upper()}] {alert.title}"

            # Create email body
            body = f"""
            Alert Details:
            
            Type: {alert.alert_type}
            Severity: {alert.severity.upper()}
            Source: {alert.source}
            Timestamp: {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}
            
            Message:
            {alert.message}
            
            """

            # Add metadata if available
            if alert.metadata:
                body += "\nAdditional Details:\n"
                for key, value in alert.metadata.items():
                    body += f"{key}: {value}\n"

            body += f"\n---\nBOLT AI Neural Agent System\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"

            msg.attach(MIMEText(body, "plain"))

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.from_email, self.to_emails, text)
            server.quit()

            logger.info(
                "Alert sent via email",
                alert_type=alert.alert_type,
                severity=alert.severity,
            )
            return True

        except Exception as e:
            logger.error("Error sending alert via email", error=str(e))
            return False


class TelegramAlertChannel:
    """Telegram alert channel"""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    async def send_alert(self, alert: Alert) -> bool:
        """Send alert to Telegram"""
        try:
            # Create message text
            severity_emoji = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}
            emoji = severity_emoji.get(alert.severity, "ℹ️")

            message_text = f"""
{emoji} *{alert.title}*

*Severity:* {alert.severity.upper()}
*Source:* {alert.source}
*Time:* {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}

{alert.message}
            """

            # Add metadata if available
            if alert.metadata:
                message_text += "\n*Details:*\n"
                for key, value in alert.metadata.items():
                    message_text += f"• {key}: {value}\n"

            message_text += f"\n_BOLT AI Neural Agent System_"

            # Send to Telegram
            payload = {
                "chat_id": self.chat_id,
                "text": message_text,
                "parse_mode": "Markdown",
            }

            response = requests.post(self.api_url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info(
                    "Alert sent to Telegram",
                    alert_type=alert.alert_type,
                    severity=alert.severity,
                )
                return True
            else:
                logger.error(
                    "Failed to send alert to Telegram",
                    status_code=response.status_code,
                    response=response.text,
                )
                return False

        except Exception as e:
            logger.error("Error sending alert to Telegram", error=str(e))
            return False


class DiscordAlertChannel:
    """Discord alert channel"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send_alert(self, alert: Alert) -> bool:
        """Send alert to Discord"""
        try:
            # Determine color based on severity
            color_map = {
                "info": 0x36A64F,  # Green
                "warning": 0xFF9500,  # Orange
                "critical": 0xFF0000,  # Red
            }
            color = color_map.get(alert.severity, 0x36A64F)

            # Create Discord embed
            embed = {
                "title": alert.title,
                "description": alert.message,
                "color": color,
                "timestamp": alert.timestamp.isoformat(),
                "fields": [
                    {
                        "name": "Severity",
                        "value": alert.severity.upper(),
                        "inline": True,
                    },
                    {"name": "Source", "value": alert.source, "inline": True},
                ],
                "footer": {"text": "BOLT AI Neural Agent System"},
            }

            # Add metadata if available
            if alert.metadata:
                metadata_text = "\n".join(
                    [f"**{k}:** {v}" for k, v in alert.metadata.items()]
                )
                embed["fields"].append(
                    {"name": "Details", "value": metadata_text, "inline": False}
                )

            # Create Discord message
            discord_message = {"embeds": [embed]}

            # Send to Discord
            response = requests.post(self.webhook_url, json=discord_message, timeout=10)

            if response.status_code in [200, 204]:
                logger.info(
                    "Alert sent to Discord",
                    alert_type=alert.alert_type,
                    severity=alert.severity,
                )
                return True
            else:
                logger.error(
                    "Failed to send alert to Discord",
                    status_code=response.status_code,
                    response=response.text,
                )
                return False

        except Exception as e:
            logger.error("Error sending alert to Discord", error=str(e))
            return False


class AlertManager:
    """Centralized alert management system"""

    def __init__(self):
        self.channels: Dict[str, AlertChannel] = {}
        self.alert_history: List[Alert] = []
        self.max_history = 1000

        # Alert filters
        self.filters = {
            "min_severity": "info",
            "rate_limits": {},  # Track rate limits per alert type
            "suppressed_alerts": set(),  # Temporarily suppressed alerts
        }

        logger.info("Alert manager initialized")

    def add_channel(self, name: str, channel: AlertChannel):
        """Add alert channel"""
        self.channels[name] = channel
        logger.info("Alert channel added", channel_name=name, enabled=channel.enabled)

    def remove_channel(self, name: str):
        """Remove alert channel"""
        if name in self.channels:
            del self.channels[name]
            logger.info("Alert channel removed", channel_name=name)

    def _should_send_alert(self, alert: Alert) -> bool:
        """Check if alert should be sent based on filters"""
        # Check minimum severity
        severity_levels = {"info": 1, "warning": 2, "critical": 3}
        min_level = severity_levels.get(self.filters["min_severity"], 1)
        alert_level = severity_levels.get(alert.severity, 1)

        if alert_level < min_level:
            return False

        # Check if alert is suppressed
        alert_key = f"{alert.alert_type}:{alert.source}"
        if alert_key in self.filters["suppressed_alerts"]:
            return False

        # Check rate limits
        if alert.alert_type in self.filters["rate_limits"]:
            rate_limit = self.filters["rate_limits"][alert.alert_type]
            now = datetime.now()

            # Remove old entries
            rate_limit["timestamps"] = [
                ts
                for ts in rate_limit["timestamps"]
                if (now - ts).total_seconds() < rate_limit["window_seconds"]
            ]

            # Check if limit exceeded
            if len(rate_limit["timestamps"]) >= rate_limit["max_count"]:
                return False

            # Add current timestamp
            rate_limit["timestamps"].append(now)

        return True

    async def send_alert(self, alert: Alert) -> bool:
        """Send alert to all enabled channels"""
        if not self._should_send_alert(alert):
            return False

        # Add to history
        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)

        # Send to all enabled channels
        success_count = 0
        total_channels = 0

        for channel_name, channel_config in self.channels.items():
            if not channel_config.enabled:
                continue

            total_channels += 1

            try:
                # Create channel instance based on type
                channel = None
                if channel_name.startswith("slack_"):
                    channel = SlackAlertChannel(
                        channel_config.config["webhook_url"],
                        channel_config.config.get("channel", "#alerts"),
                    )
                elif channel_name.startswith("email_"):
                    channel = EmailAlertChannel(
                        channel_config.config["smtp_server"],
                        channel_config.config["smtp_port"],
                        channel_config.config["username"],
                        channel_config.config["password"],
                        channel_config.config["from_email"],
                        channel_config.config["to_emails"],
                    )
                elif channel_name.startswith("telegram_"):
                    channel = TelegramAlertChannel(
                        channel_config.config["bot_token"],
                        channel_config.config["chat_id"],
                    )
                elif channel_name.startswith("discord_"):
                    channel = DiscordAlertChannel(channel_config.config["webhook_url"])

                if channel:
                    success = await channel.send_alert(alert)
                    if success:
                        success_count += 1

            except Exception as e:
                logger.error(
                    "Error sending alert to channel",
                    channel_name=channel_name,
                    error=str(e),
                )

        logger.info(
            "Alert sent",
            alert_type=alert.alert_type,
            severity=alert.severity,
            success_count=success_count,
            total_channels=total_channels,
        )

        return success_count > 0

    def create_alert(
        self,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        source: str,
        metadata: Dict[str, Any] = None,
        correlation_id: Optional[str] = None,
    ) -> Alert:
        """Create new alert"""
        return Alert(
            timestamp=datetime.now(),
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            source=source,
            metadata=metadata or {},
            correlation_id=correlation_id,
        )

    async def send_slo_violation_alert(
        self,
        slo_name: str,
        sli_name: str,
        current_value: float,
        target_value: float,
        violation_percentage: float,
        severity: str,
    ):
        """Send SLO violation alert"""
        alert = self.create_alert(
            alert_type="slo_violation",
            severity=severity,
            title=f"SLO Violation: {slo_name}",
            message=f"SLO violation detected for {sli_name}. Current value: {current_value:.2f}, Target: {target_value:.2f}, Violation: {violation_percentage:.1%}",
            source="slo_monitor",
            metadata={
                "slo_name": slo_name,
                "sli_name": sli_name,
                "current_value": current_value,
                "target_value": target_value,
                "violation_percentage": violation_percentage,
            },
        )

        return await self.send_alert(alert)

    async def send_training_alert(
        self,
        alert_type: str,
        trainer_id: str,
        message: str,
        severity: str = "warning",
        metadata: Dict[str, Any] = None,
    ):
        """Send training-related alert"""
        alert = self.create_alert(
            alert_type=alert_type,
            severity=severity,
            title=f"Training Alert: {alert_type}",
            message=message,
            source="training_system",
            metadata={"trainer_id": trainer_id, **(metadata or {})},
            correlation_id=trainer_id,
        )

        return await self.send_alert(alert)

    async def send_system_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "warning",
        metadata: Dict[str, Any] = None,
    ):
        """Send system-related alert"""
        alert = self.create_alert(
            alert_type=alert_type,
            severity=severity,
            title=f"System Alert: {alert_type}",
            message=message,
            source="system_monitor",
            metadata=metadata or {},
        )

        return await self.send_alert(alert)

    def set_rate_limit(self, alert_type: str, max_count: int, window_seconds: int):
        """Set rate limit for alert type"""
        self.filters["rate_limits"][alert_type] = {
            "max_count": max_count,
            "window_seconds": window_seconds,
            "timestamps": [],
        }
        logger.info(
            "Rate limit set",
            alert_type=alert_type,
            max_count=max_count,
            window_seconds=window_seconds,
        )

    def suppress_alert(
        self, alert_type: str, source: str, duration_seconds: int = 3600
    ):
        """Temporarily suppress alerts"""
        alert_key = f"{alert_type}:{source}"
        self.filters["suppressed_alerts"].add(alert_key)

        # Schedule unsuppression
        async def unsuppress():
            await asyncio.sleep(duration_seconds)
            self.filters["suppressed_alerts"].discard(alert_key)

        asyncio.create_task(unsuppress())
        logger.info(
            "Alert suppressed", alert_key=alert_key, duration_seconds=duration_seconds
        )

    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history"""
        recent_alerts = self.alert_history[-limit:] if limit else self.alert_history
        return [asdict(alert) for alert in recent_alerts]

    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        if not self.alert_history:
            return {"total_alerts": 0}

        # Count by severity
        severity_counts = {}
        alert_type_counts = {}

        for alert in self.alert_history:
            severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1
            alert_type_counts[alert.alert_type] = (
                alert_type_counts.get(alert.alert_type, 0) + 1
            )

        return {
            "total_alerts": len(self.alert_history),
            "severity_counts": severity_counts,
            "alert_type_counts": alert_type_counts,
            "active_channels": len([c for c in self.channels.values() if c.enabled]),
            "suppressed_alerts": len(self.filters["suppressed_alerts"]),
        }


# Global alert manager instance
alert_manager = AlertManager()


def get_alert_manager() -> AlertManager:
    """Get global alert manager instance"""
    return alert_manager
