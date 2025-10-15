import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Notification priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(Enum):
    """Notification type categories"""

    PRICE_ALERT = "price_alert"
    TRAINING_UPDATE = "training_update"
    RISK_WARNING = "risk_warning"
    SYSTEM_STATUS = "system_status"
    TRADE_SIGNAL = "trade_signal"
    ERROR = "error"
    INFO = "info"


class Notification:
    """Notification data model"""

    def __init__(
        self,
        title: str,
        message: str,
        notification_type: NotificationType,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Optional[Dict[str, Any]] = None,
        action_url: Optional[str] = None,
    ):
        self.id = f"{datetime.now().timestamp()}_{notification_type.value}"
        self.title = title
        self.message = message
        self.notification_type = notification_type
        self.priority = priority
        self.data = data or {}
        self.action_url = action_url
        self.timestamp = datetime.now()
        self.sent = False
        self.channels_sent: List[str] = []
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "type": self.notification_type.value,
            "priority": self.priority.value,
            "data": self.data,
            "action_url": self.action_url,
            "timestamp": self.timestamp.isoformat(),
            "sent": self.sent,
            "channels_sent": self.channels_sent,
            "error": self.error,
        }


class BaseNotifier(ABC):
    """
    Abstract base class for notification channels.
    Provides unified interface for sending notifications across different platforms.
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.channel_name = self.__class__.__name__.replace("Notifier", "").lower()
        self.sent_count = 0
        self.error_count = 0
        self.last_error: Optional[str] = None

    @abstractmethod
    async def send(self, notification: Notification) -> bool:
        """
        Send notification through this channel.

        Args:
            notification: Notification object to send

        Returns:
            True if sent successfully, False otherwise
        """
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Test if the notification channel is properly configured and accessible.

        Returns:
            True if connection test passes, False otherwise
        """
        pass

    async def send_notification(self, notification: Notification) -> bool:
        """
        Send notification with error handling and statistics tracking.

        Args:
            notification: Notification to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug(f"{self.channel_name} notifier is disabled")
            return False

        try:
            success = await self.send(notification)

            if success:
                self.sent_count += 1
                notification.channels_sent.append(self.channel_name)
                logger.info(
                    f"Notification sent via {self.channel_name}: {notification.title}"
                )
            else:
                self.error_count += 1
                logger.warning(f"Failed to send notification via {self.channel_name}")

            return success

        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            notification.error = str(e)
            logger.error(
                f"Error sending notification via {self.channel_name}: {str(e)}"
            )
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get notification channel statistics"""
        return {
            "channel": self.channel_name,
            "enabled": self.enabled,
            "sent_count": self.sent_count,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "success_rate": self.sent_count
            / max(self.sent_count + self.error_count, 1),
        }

    def enable(self) -> None:
        """Enable this notification channel"""
        self.enabled = True
        logger.info(f"{self.channel_name} notifier enabled")

    def disable(self) -> None:
        """Disable this notification channel"""
        self.enabled = False
        logger.info(f"{self.channel_name} notifier disabled")

    def format_message(self, notification: Notification) -> str:
        """
        Format notification message for this channel.
        Can be overridden by subclasses for channel-specific formatting.

        Args:
            notification: Notification to format

        Returns:
            Formatted message string
        """
        priority_emoji = {
            NotificationPriority.LOW: "ℹ️",
            NotificationPriority.MEDIUM: "📊",
            NotificationPriority.HIGH: "⚠️",
            NotificationPriority.CRITICAL: "🚨",
        }

        type_emoji = {
            NotificationType.PRICE_ALERT: "💰",
            NotificationType.TRAINING_UPDATE: "🧠",
            NotificationType.RISK_WARNING: "⚠️",
            NotificationType.SYSTEM_STATUS: "⚙️",
            NotificationType.TRADE_SIGNAL: "📈",
            NotificationType.ERROR: "❌",
            NotificationType.INFO: "ℹ️",
        }

        emoji = f"{priority_emoji.get(notification.priority, '')} {type_emoji.get(notification.notification_type, '')}"

        message = f"{emoji} **{notification.title}**\n\n{notification.message}"

        if notification.data:
            message += "\n\n**Details:**"
            for key, value in notification.data.items():
                message += f"\n• {key}: {value}"

        if notification.action_url:
            message += f"\n\n🔗 [View Details]({notification.action_url})"

        message += (
            f"\n\n_Timestamp: {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}_"
        )

        return message

    def should_send(self, notification: Notification) -> bool:
        """
        Determine if notification should be sent based on priority and type.
        Can be overridden by subclasses for channel-specific filtering.

        Args:
            notification: Notification to evaluate

        Returns:
            True if notification should be sent, False otherwise
        """
        # By default, send all enabled notifications
        return self.enabled

    async def batch_send(self, notifications: List[Notification]) -> Dict[str, int]:
        """
        Send multiple notifications in batch.

        Args:
            notifications: List of notifications to send

        Returns:
            Dict with success and failure counts
        """
        results = {"success": 0, "failed": 0, "skipped": 0}

        for notification in notifications:
            if not self.should_send(notification):
                results["skipped"] += 1
                continue

            success = await self.send_notification(notification)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1

        return results
