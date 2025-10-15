"""
Critical Event Detection Service
Detects and tags critical market events for priority boosting in experience replay
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of critical events."""

    VOLATILITY_SPIKE = "volatility_spike"
    REGIME_SWITCH = "regime_switch"
    NEWS_IMPACT = "news_impact"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    FLASH_CRASH = "flash_crash"
    PUMP_DUMP = "pump_dump"
    BREAKOUT = "breakout"
    REVERSAL = "reversal"


@dataclass
class CriticalEvent:
    """Critical event detection result."""

    event_type: EventType
    timestamp: datetime
    symbol: str
    severity: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    description: str
    metadata: Dict[str, Any]
    priority_boost: float = 1.0


class EventDetector:
    """
    Detects critical market events for experience replay priority boosting.

    Features:
    - Volatility spike detection
    - Regime switch identification
    - News impact assessment
    - Liquidity crisis detection
    - Flash crash detection
    - Pattern recognition (breakouts, reversals)
    """

    def __init__(
        self,
        volatility_threshold: float = 3.0,
        regime_change_threshold: float = 0.7,
        flash_crash_threshold: float = 0.1,
        news_impact_threshold: float = 0.5,
        lookback_window: int = 100,
    ):
        """
        Initialize event detector.

        Args:
            volatility_threshold: Standard deviations for volatility spike
            regime_change_threshold: Threshold for regime change detection
            flash_crash_threshold: Percentage change for flash crash
            news_impact_threshold: Threshold for news impact
            lookback_window: Number of periods to look back for analysis
        """
        self.volatility_threshold = volatility_threshold
        self.regime_change_threshold = regime_change_threshold
        self.flash_crash_threshold = flash_crash_threshold
        self.news_impact_threshold = news_impact_threshold
        self.lookback_window = lookback_window

        # State tracking
        self.price_history = {}
        self.volume_history = {}
        self.volatility_history = {}
        self.regime_history = {}

        # Statistics
        self.total_events_detected = 0
        self.events_by_type = {event_type: 0 for event_type in EventType}

        logger.info(
            f"EventDetector initialized: volatility_threshold={volatility_threshold}, "
            f"regime_change_threshold={regime_change_threshold}, "
            f"flash_crash_threshold={flash_crash_threshold}"
        )

    def detect_events(
        self,
        symbol: str,
        price_data: np.ndarray,
        volume_data: np.ndarray,
        timestamp: datetime,
        news_sentiment: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[CriticalEvent]:
        """
        Detect critical events for given market data.

        Args:
            symbol: Trading symbol
            price_data: Price data array (OHLC or close prices)
            volume_data: Volume data array
            timestamp: Current timestamp
            news_sentiment: News sentiment score (-1 to 1)
            metadata: Additional metadata

        Returns:
            List of detected critical events
        """
        events = []

        # Update history
        self._update_history(symbol, price_data, volume_data, timestamp)

        # Detect different types of events
        events.extend(self._detect_volatility_spike(symbol, price_data, timestamp))
        events.extend(self._detect_regime_switch(symbol, price_data, timestamp))
        events.extend(self._detect_flash_crash(symbol, price_data, timestamp))
        events.extend(self._detect_breakout(symbol, price_data, timestamp))
        events.extend(self._detect_reversal(symbol, price_data, timestamp))

        # News impact detection
        if news_sentiment is not None:
            events.extend(
                self._detect_news_impact(symbol, price_data, news_sentiment, timestamp)
            )

        # Update statistics
        self.total_events_detected += len(events)
        for event in events:
            self.events_by_type[event.event_type] += 1

        return events

    def _update_history(
        self,
        symbol: str,
        price_data: np.ndarray,
        volume_data: np.ndarray,
        timestamp: datetime,
    ) -> None:
        """Update historical data for event detection."""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
            self.volume_history[symbol] = []
            self.volatility_history[symbol] = []
            self.regime_history[symbol] = []

        # Add new data point
        self.price_history[symbol].append(
            {"timestamp": timestamp, "data": price_data.copy()}
        )

        self.volume_history[symbol].append(
            {"timestamp": timestamp, "data": volume_data.copy()}
        )

        # Calculate volatility
        if len(self.price_history[symbol]) >= 2:
            returns = np.diff([p["data"] for p in self.price_history[symbol][-2:]])
            volatility = np.std(returns)
            self.volatility_history[symbol].append(
                {"timestamp": timestamp, "volatility": volatility}
            )

        # Keep only recent history
        max_history = self.lookback_window * 2
        if len(self.price_history[symbol]) > max_history:
            self.price_history[symbol] = self.price_history[symbol][-max_history:]
            self.volume_history[symbol] = self.volume_history[symbol][-max_history:]
            self.volatility_history[symbol] = self.volatility_history[symbol][
                -max_history:
            ]

    def _detect_volatility_spike(
        self, symbol: str, price_data: np.ndarray, timestamp: datetime
    ) -> List[CriticalEvent]:
        """Detect volatility spikes."""
        events = []

        if (
            symbol not in self.volatility_history
            or len(self.volatility_history[symbol]) < 10
        ):
            return events

        # Get recent volatility
        recent_volatilities = [
            v["volatility"] for v in self.volatility_history[symbol][-20:]
        ]
        current_volatility = recent_volatilities[-1]

        # Calculate volatility statistics
        mean_volatility = np.mean(recent_volatilities[:-1])
        std_volatility = np.std(recent_volatilities[:-1])

        # Check for spike
        if std_volatility > 0:
            z_score = (current_volatility - mean_volatility) / std_volatility

            if z_score > self.volatility_threshold:
                severity = min(z_score / self.volatility_threshold, 1.0)
                confidence = min(z_score / (self.volatility_threshold * 2), 1.0)

                event = CriticalEvent(
                    event_type=EventType.VOLATILITY_SPIKE,
                    timestamp=timestamp,
                    symbol=symbol,
                    severity=severity,
                    confidence=confidence,
                    description=f"Volatility spike detected: {z_score:.2f}σ above mean",
                    metadata={
                        "z_score": z_score,
                        "current_volatility": current_volatility,
                        "mean_volatility": mean_volatility,
                        "std_volatility": std_volatility,
                    },
                    priority_boost=1.0 + severity * 2.0,
                )
                events.append(event)

        return events

    def _detect_regime_switch(
        self, symbol: str, price_data: np.ndarray, timestamp: datetime
    ) -> List[CriticalEvent]:
        """Detect regime switches (bull/bear/sideways)."""
        events = []

        if symbol not in self.price_history or len(self.price_history[symbol]) < 50:
            return events

        # Get recent price data
        recent_prices = [p["data"] for p in self.price_history[symbol][-50:]]

        # Calculate moving averages
        short_ma = np.mean(recent_prices[-10:])
        long_ma = np.mean(recent_prices[-30:])

        # Determine current regime
        if short_ma > long_ma * 1.02:
            current_regime = "bull"
        elif short_ma < long_ma * 0.98:
            current_regime = "bear"
        else:
            current_regime = "sideways"

        # Check for regime change
        if symbol in self.regime_history:
            previous_regime = (
                self.regime_history[symbol][-1] if self.regime_history[symbol] else None
            )

            if previous_regime and previous_regime != current_regime:
                # Regime change detected
                severity = 0.8  # High severity for regime changes
                confidence = 0.7

                event = CriticalEvent(
                    event_type=EventType.REGIME_SWITCH,
                    timestamp=timestamp,
                    symbol=symbol,
                    severity=severity,
                    confidence=confidence,
                    description=f"Regime switch: {previous_regime} → {current_regime}",
                    metadata={
                        "previous_regime": previous_regime,
                        "current_regime": current_regime,
                        "short_ma": short_ma,
                        "long_ma": long_ma,
                    },
                    priority_boost=2.0,
                )
                events.append(event)

        # Update regime history
        self.regime_history[symbol].append(current_regime)
        if len(self.regime_history[symbol]) > 100:
            self.regime_history[symbol] = self.regime_history[symbol][-100:]

        return events

    def _detect_flash_crash(
        self, symbol: str, price_data: np.ndarray, timestamp: datetime
    ) -> List[CriticalEvent]:
        """Detect flash crashes (sudden large price drops)."""
        events = []

        if symbol not in self.price_history or len(self.price_history[symbol]) < 5:
            return events

        # Get recent prices
        recent_prices = [p["data"] for p in self.price_history[symbol][-5:]]
        current_price = recent_prices[-1]
        previous_price = recent_prices[-2]

        # Calculate percentage change
        price_change = (current_price - previous_price) / previous_price

        # Check for flash crash
        if price_change < -self.flash_crash_threshold:
            severity = min(abs(price_change) / self.flash_crash_threshold, 1.0)
            confidence = 0.9  # High confidence for large price drops

            event = CriticalEvent(
                event_type=EventType.FLASH_CRASH,
                timestamp=timestamp,
                symbol=symbol,
                severity=severity,
                confidence=confidence,
                description=f"Flash crash detected: {price_change:.2%} drop",
                metadata={
                    "price_change": price_change,
                    "current_price": current_price,
                    "previous_price": previous_price,
                },
                priority_boost=1.0 + severity * 3.0,
            )
            events.append(event)

        return events

    def _detect_breakout(
        self, symbol: str, price_data: np.ndarray, timestamp: datetime
    ) -> List[CriticalEvent]:
        """Detect breakouts (price breaking through key levels)."""
        events = []

        if symbol not in self.price_history or len(self.price_history[symbol]) < 20:
            return events

        # Get recent prices
        recent_prices = [p["data"] for p in self.price_history[symbol][-20:]]
        current_price = recent_prices[-1]

        # Calculate support and resistance levels
        high_prices = [
            max(p) if isinstance(p, (list, np.ndarray)) else p for p in recent_prices
        ]
        low_prices = [
            min(p) if isinstance(p, (list, np.ndarray)) else p for p in recent_prices
        ]

        resistance = np.percentile(high_prices, 90)
        support = np.percentile(low_prices, 10)

        # Check for breakout
        if current_price > resistance * 1.01:  # Breakout above resistance
            severity = 0.7
            confidence = 0.8

            event = CriticalEvent(
                event_type=EventType.BREAKOUT,
                timestamp=timestamp,
                symbol=symbol,
                severity=severity,
                confidence=confidence,
                description=f"Breakout above resistance: {current_price:.4f} > {resistance:.4f}",
                metadata={
                    "current_price": current_price,
                    "resistance": resistance,
                    "breakout_type": "above_resistance",
                },
                priority_boost=1.5,
            )
            events.append(event)

        elif current_price < support * 0.99:  # Breakdown below support
            severity = 0.7
            confidence = 0.8

            event = CriticalEvent(
                event_type=EventType.BREAKOUT,
                timestamp=timestamp,
                symbol=symbol,
                severity=severity,
                confidence=confidence,
                description=f"Breakdown below support: {current_price:.4f} < {support:.4f}",
                metadata={
                    "current_price": current_price,
                    "support": support,
                    "breakout_type": "below_support",
                },
                priority_boost=1.5,
            )
            events.append(event)

        return events

    def _detect_reversal(
        self, symbol: str, price_data: np.ndarray, timestamp: datetime
    ) -> List[CriticalEvent]:
        """Detect price reversals."""
        events = []

        if symbol not in self.price_history or len(self.price_history[symbol]) < 10:
            return events

        # Get recent prices
        recent_prices = [p["data"] for p in self.price_history[symbol][-10:]]

        # Calculate trend
        if len(recent_prices) >= 5:
            early_trend = np.mean(recent_prices[-5:-2]) - np.mean(recent_prices[-8:-5])
            recent_trend = np.mean(recent_prices[-2:]) - np.mean(recent_prices[-5:-2])

            # Check for trend reversal
            if early_trend > 0 and recent_trend < 0:  # Bullish to bearish
                severity = 0.6
                confidence = 0.7

                event = CriticalEvent(
                    event_type=EventType.REVERSAL,
                    timestamp=timestamp,
                    symbol=symbol,
                    severity=severity,
                    confidence=confidence,
                    description="Trend reversal: Bullish → Bearish",
                    metadata={
                        "early_trend": early_trend,
                        "recent_trend": recent_trend,
                        "reversal_type": "bullish_to_bearish",
                    },
                    priority_boost=1.3,
                )
                events.append(event)

            elif early_trend < 0 and recent_trend > 0:  # Bearish to bullish
                severity = 0.6
                confidence = 0.7

                event = CriticalEvent(
                    event_type=EventType.REVERSAL,
                    timestamp=timestamp,
                    symbol=symbol,
                    severity=severity,
                    confidence=confidence,
                    description="Trend reversal: Bearish → Bullish",
                    metadata={
                        "early_trend": early_trend,
                        "recent_trend": recent_trend,
                        "reversal_type": "bearish_to_bullish",
                    },
                    priority_boost=1.3,
                )
                events.append(event)

        return events

    def _detect_news_impact(
        self,
        symbol: str,
        price_data: np.ndarray,
        news_sentiment: float,
        timestamp: datetime,
    ) -> List[CriticalEvent]:
        """Detect news impact on price."""
        events = []

        if symbol not in self.price_history or len(self.price_history[symbol]) < 5:
            return events

        # Get recent prices
        recent_prices = [p["data"] for p in self.price_history[symbol][-5:]]
        current_price = recent_prices[-1]
        previous_price = recent_prices[-2]

        # Calculate price change
        price_change = (current_price - previous_price) / previous_price

        # Check for news impact
        if abs(news_sentiment) > self.news_impact_threshold:
            # Expected direction based on sentiment
            expected_direction = 1 if news_sentiment > 0 else -1
            actual_direction = 1 if price_change > 0 else -1

            # Check if price moved in expected direction
            if expected_direction == actual_direction:
                severity = min(abs(news_sentiment), 1.0)
                confidence = 0.8

                event = CriticalEvent(
                    event_type=EventType.NEWS_IMPACT,
                    timestamp=timestamp,
                    symbol=symbol,
                    severity=severity,
                    confidence=confidence,
                    description=f"News impact: sentiment={news_sentiment:.2f}, price_change={price_change:.2%}",
                    metadata={
                        "news_sentiment": news_sentiment,
                        "price_change": price_change,
                        "expected_direction": expected_direction,
                        "actual_direction": actual_direction,
                    },
                    priority_boost=1.0 + severity,
                )
                events.append(event)

        return events

    def get_stats(self) -> Dict[str, Any]:
        """Get event detection statistics."""
        return {
            "total_events_detected": self.total_events_detected,
            "events_by_type": {
                event_type.value: count
                for event_type, count in self.events_by_type.items()
            },
            "symbols_tracked": len(self.price_history),
            "lookback_window": self.lookback_window,
            "thresholds": {
                "volatility_threshold": self.volatility_threshold,
                "regime_change_threshold": self.regime_change_threshold,
                "flash_crash_threshold": self.flash_crash_threshold,
                "news_impact_threshold": self.news_impact_threshold,
            },
        }

    def clear_history(self, symbol: Optional[str] = None) -> None:
        """Clear historical data."""
        if symbol:
            if symbol in self.price_history:
                del self.price_history[symbol]
            if symbol in self.volume_history:
                del self.volume_history[symbol]
            if symbol in self.volatility_history:
                del self.volatility_history[symbol]
            if symbol in self.regime_history:
                del self.regime_history[symbol]
        else:
            self.price_history.clear()
            self.volume_history.clear()
            self.volatility_history.clear()
            self.regime_history.clear()

        logger.info(
            f"Cleared history for {'all symbols' if symbol is None else symbol}"
        )
