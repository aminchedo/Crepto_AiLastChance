import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from db.redis_client import redis_client
from models.alert import (Alert, AlertChannel, AlertHistory, AlertStatus,
                          AlertType)
from models.user import User
from monitoring.metrics import record_alert
from services.market_service import MarketService
from services.signal_service import signal_service
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class AlertService:
    """Real-time alert system with multiple delivery channels."""

    def __init__(self):
        self.market_service = MarketService()
        self.active_alerts: Dict[int, Alert] = {}
        self.alert_check_interval = 30  # Check alerts every 30 seconds
        self.is_running = False

    async def start_alert_monitoring(self):
        """Start the alert monitoring service."""
        if self.is_running:
            return

        self.is_running = True
        logger.info("Starting alert monitoring service")

        # Start background task
        asyncio.create_task(self._monitor_alerts())

    async def stop_alert_monitoring(self):
        """Stop the alert monitoring service."""
        self.is_running = False
        logger.info("Alert monitoring service stopped")

    async def create_alert(
        self,
        db: AsyncSession,
        user_id: int,
        symbol: str,
        alert_type: AlertType,
        threshold_value: Optional[float] = None,
        channels: List[AlertChannel] = None,
        message: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Alert:
        """Create a new alert."""
        if channels is None:
            channels = [AlertChannel.WEBSOCKET]

        alert = Alert(
            user_id=user_id,
            symbol=symbol,
            alert_type=alert_type,
            threshold_value=threshold_value,
            channels=channels,
            message=message
            or self._generate_default_message(alert_type, symbol, threshold_value),
            expires_at=expires_at,
            status=AlertStatus.ACTIVE,
        )

        db.add(alert)
        await db.commit()
        await db.refresh(alert)

        # Add to active alerts
        self.active_alerts[alert.id] = alert

        logger.info(f"Created alert {alert.id} for user {user_id}, symbol {symbol}")
        return alert

    async def update_alert(
        self, db: AsyncSession, alert_id: int, user_id: int, **updates
    ) -> Optional[Alert]:
        """Update an existing alert."""
        result = await db.execute(
            select(Alert).where(and_(Alert.id == alert_id, Alert.user_id == user_id))
        )
        alert = result.scalar_one_or_none()

        if not alert:
            return None

        # Update fields
        for key, value in updates.items():
            if hasattr(alert, key):
                setattr(alert, key, value)

        await db.commit()
        await db.refresh(alert)

        # Update active alerts
        if alert.status == AlertStatus.ACTIVE:
            self.active_alerts[alert.id] = alert
        elif alert.id in self.active_alerts:
            del self.active_alerts[alert.id]

        return alert

    async def delete_alert(self, db: AsyncSession, alert_id: int, user_id: int) -> bool:
        """Delete an alert."""
        result = await db.execute(
            select(Alert).where(and_(Alert.id == alert_id, Alert.user_id == user_id))
        )
        alert = result.scalar_one_or_none()

        if not alert:
            return False

        await db.delete(alert)
        await db.commit()

        # Remove from active alerts
        if alert.id in self.active_alerts:
            del self.active_alerts[alert.id]

        logger.info(f"Deleted alert {alert_id} for user {user_id}")
        return True

    async def get_user_alerts(
        self, db: AsyncSession, user_id: int, status: Optional[AlertStatus] = None
    ) -> List[Alert]:
        """Get alerts for a user."""
        query = select(Alert).where(Alert.user_id == user_id)

        if status:
            query = query.where(Alert.status == status)

        result = await db.execute(query)
        return result.scalars().all()

    async def _monitor_alerts(self):
        """Background task to monitor alerts."""
        while self.is_running:
            try:
                await self._check_all_alerts()
                await asyncio.sleep(self.alert_check_interval)
            except Exception as e:
                logger.error(f"Error in alert monitoring: {e}")
                await asyncio.sleep(self.alert_check_interval)

    async def _check_all_alerts(self):
        """Check all active alerts for triggers."""
        if not self.active_alerts:
            return

        # Get current market data for all symbols
        symbols = list(set(alert.symbol for alert in self.active_alerts.values()))
        market_data = {}

        for symbol in symbols:
            try:
                # Get current price
                candlestick_data = await self.market_service.get_candlestick_data(
                    symbol, "1h", 1
                )
                if candlestick_data:
                    market_data[symbol] = {
                        "price": candlestick_data[-1]["close"],
                        "timestamp": datetime.fromtimestamp(
                            candlestick_data[-1]["time"] / 1000
                        ),
                    }

                # Get AI signals
                signals = await signal_service.generate_signals(
                    symbol, "1h", "combined"
                )
                if signals:
                    market_data[symbol]["signal"] = signals[-1]

            except Exception as e:
                logger.error(f"Error getting market data for {symbol}: {e}")
                continue

        # Check each alert
        for alert_id, alert in list(self.active_alerts.items()):
            try:
                await self._check_alert(alert, market_data)
            except Exception as e:
                logger.error(f"Error checking alert {alert_id}: {e}")

    async def _check_alert(self, alert: Alert, market_data: Dict):
        """Check if an alert should be triggered."""
        symbol_data = market_data.get(alert.symbol)
        if not symbol_data:
            return

        current_price = symbol_data["price"]
        current_signal = symbol_data.get("signal")

        should_trigger = False
        triggered_value = None
        message = alert.message

        # Check alert conditions
        if alert.alert_type == AlertType.PRICE_ABOVE:
            if current_price > alert.threshold_value:
                should_trigger = True
                triggered_value = current_price
                message = f"{alert.symbol} price ({current_price:.2f}) is above {alert.threshold_value:.2f}"

        elif alert.alert_type == AlertType.PRICE_BELOW:
            if current_price < alert.threshold_value:
                should_trigger = True
                triggered_value = current_price
                message = f"{alert.symbol} price ({current_price:.2f}) is below {alert.threshold_value:.2f}"

        elif alert.alert_type == AlertType.PRICE_CHANGE:
            # Check for significant price change (threshold_value is percentage)
            if alert.condition_params and "previous_price" in alert.condition_params:
                previous_price = alert.condition_params["previous_price"]
                change_percent = (
                    (current_price - previous_price) / previous_price
                ) * 100

                if abs(change_percent) >= alert.threshold_value:
                    should_trigger = True
                    triggered_value = change_percent
                    message = f"{alert.symbol} price changed by {change_percent:.2f}%"

        elif alert.alert_type == AlertType.AI_SIGNAL:
            if current_signal and current_signal["signal_type"] != "HOLD":
                if current_signal["score"] >= alert.threshold_value:
                    should_trigger = True
                    triggered_value = current_signal["score"]
                    message = f"AI Signal: {alert.symbol} {current_signal['signal_type']} (score: {current_signal['score']:.1f})"

        elif alert.alert_type == AlertType.TECHNICAL_PATTERN:
            if current_signal and current_signal["signal_type"] != "HOLD":
                should_trigger = True
                triggered_value = current_signal["score"]
                message = f"Technical Pattern: {alert.symbol} {current_signal['signal_type']} detected"

        elif alert.alert_type == AlertType.VOLUME_SPIKE:
            # Check for volume spike (would need volume data)
            if alert.condition_params and "volume_threshold" in alert.condition_params:
                # This would require volume data from market service
                pass

        # Trigger alert if conditions are met
        if should_trigger:
            await self._trigger_alert(alert, triggered_value, message)

    async def _trigger_alert(
        self, alert: Alert, triggered_value: Optional[float], message: str
    ):
        """Trigger an alert and send notifications."""
        try:
            # Create alert history record
            alert_history = AlertHistory(
                alert_id=alert.id,
                triggered_value=triggered_value,
                message=message,
                channels_sent=alert.channels,
                delivery_status={channel: "pending" for channel in alert.channels},
            )

            # Send notifications to all channels
            delivery_status = {}
            for channel in alert.channels:
                try:
                    success = await self._send_notification(alert, message, channel)
                    delivery_status[channel] = "success" if success else "failed"
                except Exception as e:
                    logger.error(f"Failed to send {channel} notification: {e}")
                    delivery_status[channel] = "failed"

            alert_history.delivery_status = delivery_status

            # Update alert
            alert.trigger_count += 1
            alert.last_triggered_at = datetime.utcnow()

            # Record metrics
            record_alert(
                alert_type=alert.alert_type.value,
                symbol=alert.symbol,
                channel=channel,
                delivered=delivery_status.get(channel) == "success",
            )

            logger.info(f"Triggered alert {alert.id}: {message}")

        except Exception as e:
            logger.error(f"Error triggering alert {alert.id}: {e}")

    async def _send_notification(
        self, alert: Alert, message: str, channel: AlertChannel
    ) -> bool:
        """Send notification via specified channel."""
        try:
            if channel == AlertChannel.WEBSOCKET:
                return await self._send_websocket_notification(alert, message)
            elif channel == AlertChannel.TELEGRAM:
                return await self._send_telegram_notification(alert, message)
            elif channel == AlertChannel.EMAIL:
                return await self._send_email_notification(alert, message)
            else:
                logger.warning(f"Unknown notification channel: {channel}")
                return False
        except Exception as e:
            logger.error(f"Error sending {channel} notification: {e}")
            return False

    async def _send_websocket_notification(self, alert: Alert, message: str) -> bool:
        """Send WebSocket notification."""
        try:
            # Store notification in Redis for WebSocket service to pick up
            notification = {
                "type": "alert",
                "user_id": alert.user_id,
                "alert_id": alert.id,
                "symbol": alert.symbol,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
            }

            await redis_client.set(
                f"ws_notification:{alert.user_id}:{alert.id}",
                notification,
                expire=300,  # 5 minutes TTL
            )

            return True
        except Exception as e:
            logger.error(f"WebSocket notification error: {e}")
            return False

    async def _send_telegram_notification(self, alert: Alert, message: str) -> bool:
        """Send Telegram notification."""
        try:
            # Get user's Telegram chat ID
            from db.database import AsyncSessionLocal

            async with AsyncSessionLocal() as db:
                result = await db.execute(select(User).where(User.id == alert.user_id))
                user = result.scalar_one_or_none()

                if not user or not user.telegram_chat_id or not user.telegram_enabled:
                    return False

                # Send Telegram message (would need Telegram bot integration)
                # This is a placeholder - actual implementation would use python-telegram-bot
                logger.info(
                    f"Telegram notification to {user.telegram_chat_id}: {message}"
                )
                return True

        except Exception as e:
            logger.error(f"Telegram notification error: {e}")
            return False

    async def _send_email_notification(self, alert: Alert, message: str) -> bool:
        """Send email notification."""
        try:
            # Get user's email
            from db.database import AsyncSessionLocal

            async with AsyncSessionLocal() as db:
                result = await db.execute(select(User).where(User.id == alert.user_id))
                user = result.scalar_one_or_none()

                if not user or not user.email_enabled:
                    return False

                # Send email (would need SMTP integration)
                # This is a placeholder - actual implementation would use smtplib
                logger.info(f"Email notification to {user.email}: {message}")
                return True

        except Exception as e:
            logger.error(f"Email notification error: {e}")
            return False

    def _generate_default_message(
        self, alert_type: AlertType, symbol: str, threshold_value: Optional[float]
    ) -> str:
        """Generate default alert message."""
        if alert_type == AlertType.PRICE_ABOVE:
            return f"{symbol} price is above {threshold_value:.2f}"
        elif alert_type == AlertType.PRICE_BELOW:
            return f"{symbol} price is below {threshold_value:.2f}"
        elif alert_type == AlertType.PRICE_CHANGE:
            return f"{symbol} price changed by {threshold_value:.2f}%"
        elif alert_type == AlertType.AI_SIGNAL:
            return f"AI signal detected for {symbol}"
        elif alert_type == AlertType.TECHNICAL_PATTERN:
            return f"Technical pattern detected for {symbol}"
        elif alert_type == AlertType.VOLUME_SPIKE:
            return f"Volume spike detected for {symbol}"
        else:
            return f"Alert triggered for {symbol}"


# Global alert service instance
alert_service = AlertService()
