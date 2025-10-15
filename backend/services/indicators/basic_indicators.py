"""
Basic Technical Indicators
Implementation of fundamental technical analysis indicators
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class IndicatorResult:
    """Result of indicator calculation."""

    values: np.ndarray
    signals: Optional[np.ndarray] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseIndicator(ABC):
    """Base class for all technical indicators."""

    def __init__(self, name: str, period: int = 14):
        self.name = name
        self.period = period

    @abstractmethod
    def calculate(self, data: np.ndarray, **kwargs) -> IndicatorResult:
        """Calculate indicator values."""
        pass

    def validate_data(self, data: np.ndarray, min_length: int = None) -> bool:
        """Validate input data."""
        if min_length is None:
            min_length = self.period

        if len(data) < min_length:
            logger.warning(
                f"Insufficient data for {self.name}: {len(data)} < {min_length}"
            )
            return False

        if np.any(np.isnan(data)) or np.any(np.isinf(data)):
            logger.warning(f"Invalid data detected in {self.name}")
            return False

        return True


class SMA(BaseIndicator):
    """Simple Moving Average."""

    def __init__(self, period: int = 20):
        super().__init__("SMA", period)

    def calculate(self, data: np.ndarray, **kwargs) -> IndicatorResult:
        """Calculate Simple Moving Average."""
        if not self.validate_data(data):
            return IndicatorResult(values=np.array([]))

        sma_values = np.full(len(data), np.nan)

        for i in range(self.period - 1, len(data)):
            sma_values[i] = np.mean(data[i - self.period + 1 : i + 1])

        return IndicatorResult(values=sma_values)


class EMA(BaseIndicator):
    """Exponential Moving Average."""

    def __init__(self, period: int = 20):
        super().__init__("EMA", period)
        self.alpha = 2.0 / (period + 1)

    def calculate(self, data: np.ndarray, **kwargs) -> IndicatorResult:
        """Calculate Exponential Moving Average."""
        if not self.validate_data(data):
            return IndicatorResult(values=np.array([]))

        ema_values = np.full(len(data), np.nan)
        ema_values[self.period - 1] = np.mean(data[: self.period])

        for i in range(self.period, len(data)):
            ema_values[i] = self.alpha * data[i] + (1 - self.alpha) * ema_values[i - 1]

        return IndicatorResult(values=ema_values)


class RSI(BaseIndicator):
    """Relative Strength Index."""

    def __init__(self, period: int = 14):
        super().__init__("RSI", period)

    def calculate(self, data: np.ndarray, **kwargs) -> IndicatorResult:
        """Calculate Relative Strength Index."""
        if not self.validate_data(data, self.period + 1):
            return IndicatorResult(values=np.array([]))

        # Calculate price changes
        price_changes = np.diff(data)

        # Separate gains and losses
        gains = np.where(price_changes > 0, price_changes, 0)
        losses = np.where(price_changes < 0, -price_changes, 0)

        # Calculate average gains and losses
        avg_gains = np.full(len(data), np.nan)
        avg_losses = np.full(len(data), np.nan)

        # Initial average
        avg_gains[self.period] = np.mean(gains[: self.period])
        avg_losses[self.period] = np.mean(losses[: self.period])

        # Calculate RSI
        rsi_values = np.full(len(data), np.nan)

        for i in range(self.period + 1, len(data)):
            # Update averages using Wilder's smoothing
            avg_gains[i] = (
                avg_gains[i - 1] * (self.period - 1) + gains[i - 1]
            ) / self.period
            avg_losses[i] = (
                avg_losses[i - 1] * (self.period - 1) + losses[i - 1]
            ) / self.period

            # Calculate RSI
            if avg_losses[i] == 0:
                rsi_values[i] = 100
            else:
                rs = avg_gains[i] / avg_losses[i]
                rsi_values[i] = 100 - (100 / (1 + rs))

        # Generate signals
        signals = np.full(len(data), 0)
        signals[rsi_values > 70] = -1  # Overbought
        signals[rsi_values < 30] = 1  # Oversold

        return IndicatorResult(
            values=rsi_values,
            signals=signals,
            metadata={"overbought": 70, "oversold": 30},
        )


class MACD(BaseIndicator):
    """Moving Average Convergence Divergence."""

    def __init__(
        self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9
    ):
        super().__init__("MACD", slow_period)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate(self, data: np.ndarray, **kwargs) -> IndicatorResult:
        """Calculate MACD."""
        if not self.validate_data(data, self.slow_period):
            return IndicatorResult(values=np.array([]))

        # Calculate EMAs
        fast_ema = EMA(self.fast_period).calculate(data).values
        slow_ema = EMA(self.slow_period).calculate(data).values

        # Calculate MACD line
        macd_line = fast_ema - slow_ema

        # Calculate signal line
        signal_line = EMA(self.signal_period).calculate(macd_line).values

        # Calculate histogram
        histogram = macd_line - signal_line

        # Generate signals
        signals = np.full(len(data), 0)
        for i in range(1, len(data)):
            if macd_line[i] > signal_line[i] and macd_line[i - 1] <= signal_line[i - 1]:
                signals[i] = 1  # Bullish crossover
            elif (
                macd_line[i] < signal_line[i] and macd_line[i - 1] >= signal_line[i - 1]
            ):
                signals[i] = -1  # Bearish crossover

        return IndicatorResult(
            values=macd_line,
            signals=signals,
            metadata={
                "macd_line": macd_line,
                "signal_line": signal_line,
                "histogram": histogram,
                "fast_period": self.fast_period,
                "slow_period": self.slow_period,
                "signal_period": self.signal_period,
            },
        )


class Stochastic(BaseIndicator):
    """Stochastic Oscillator."""

    def __init__(self, k_period: int = 14, d_period: int = 3):
        super().__init__("Stochastic", k_period)
        self.k_period = k_period
        self.d_period = d_period

    def calculate(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray, **kwargs
    ) -> IndicatorResult:
        """Calculate Stochastic Oscillator."""
        if not self.validate_data(close, self.k_period):
            return IndicatorResult(values=np.array([]))

        # Calculate %K
        k_values = np.full(len(close), np.nan)

        for i in range(self.k_period - 1, len(close)):
            period_high = np.max(high[i - self.k_period + 1 : i + 1])
            period_low = np.min(low[i - self.k_period + 1 : i + 1])

            if period_high != period_low:
                k_values[i] = 100 * (close[i] - period_low) / (period_high - period_low)
            else:
                k_values[i] = 50

        # Calculate %D (moving average of %K)
        d_values = SMA(self.d_period).calculate(k_values).values

        # Generate signals
        signals = np.full(len(close), 0)
        signals[k_values > 80] = -1  # Overbought
        signals[k_values < 20] = 1  # Oversold

        return IndicatorResult(
            values=k_values,
            signals=signals,
            metadata={
                "k_values": k_values,
                "d_values": d_values,
                "overbought": 80,
                "oversold": 20,
            },
        )


class ATR(BaseIndicator):
    """Average True Range."""

    def __init__(self, period: int = 14):
        super().__init__("ATR", period)

    def calculate(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray, **kwargs
    ) -> IndicatorResult:
        """Calculate Average True Range."""
        if not self.validate_data(close, self.period + 1):
            return IndicatorResult(values=np.array([]))

        # Calculate True Range
        tr_values = np.full(len(close), np.nan)

        for i in range(1, len(close)):
            tr1 = high[i] - low[i]
            tr2 = abs(high[i] - close[i - 1])
            tr3 = abs(low[i] - close[i - 1])
            tr_values[i] = max(tr1, tr2, tr3)

        # Calculate ATR using EMA
        atr_values = EMA(self.period).calculate(tr_values).values

        return IndicatorResult(values=atr_values)


class OBV(BaseIndicator):
    """On Balance Volume."""

    def __init__(self):
        super().__init__("OBV", 1)

    def calculate(
        self, close: np.ndarray, volume: np.ndarray, **kwargs
    ) -> IndicatorResult:
        """Calculate On Balance Volume."""
        if not self.validate_data(close, 2):
            return IndicatorResult(values=np.array([]))

        obv_values = np.zeros(len(close))
        obv_values[0] = volume[0]

        for i in range(1, len(close)):
            if close[i] > close[i - 1]:
                obv_values[i] = obv_values[i - 1] + volume[i]
            elif close[i] < close[i - 1]:
                obv_values[i] = obv_values[i - 1] - volume[i]
            else:
                obv_values[i] = obv_values[i - 1]

        return IndicatorResult(values=obv_values)


class VWAP(BaseIndicator):
    """Volume Weighted Average Price."""

    def __init__(self):
        super().__init__("VWAP", 1)

    def calculate(
        self,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray,
        **kwargs,
    ) -> IndicatorResult:
        """Calculate Volume Weighted Average Price."""
        if not self.validate_data(close, 1):
            return IndicatorResult(values=np.array([]))

        # Calculate typical price
        typical_price = (high + low + close) / 3

        # Calculate cumulative volume and price
        cumulative_volume = np.cumsum(volume)
        cumulative_price_volume = np.cumsum(typical_price * volume)

        # Calculate VWAP
        vwap_values = np.full(len(close), np.nan)
        for i in range(len(close)):
            if cumulative_volume[i] > 0:
                vwap_values[i] = cumulative_price_volume[i] / cumulative_volume[i]

        return IndicatorResult(values=vwap_values)


class BollingerBands(BaseIndicator):
    """Bollinger Bands."""

    def __init__(self, period: int = 20, std_dev: float = 2.0):
        super().__init__("BollingerBands", period)
        self.std_dev = std_dev

    def calculate(self, data: np.ndarray, **kwargs) -> IndicatorResult:
        """Calculate Bollinger Bands."""
        if not self.validate_data(data):
            return IndicatorResult(values=np.array([]))

        # Calculate SMA
        sma_values = SMA(self.period).calculate(data).values

        # Calculate standard deviation
        std_values = np.full(len(data), np.nan)
        for i in range(self.period - 1, len(data)):
            std_values[i] = np.std(data[i - self.period + 1 : i + 1])

        # Calculate bands
        upper_band = sma_values + (self.std_dev * std_values)
        lower_band = sma_values - (self.std_dev * std_values)

        # Calculate %B (position within bands)
        percent_b = np.full(len(data), np.nan)
        for i in range(len(data)):
            if not np.isnan(upper_band[i]) and not np.isnan(lower_band[i]):
                if upper_band[i] != lower_band[i]:
                    percent_b[i] = (data[i] - lower_band[i]) / (
                        upper_band[i] - lower_band[i]
                    )
                else:
                    percent_b[i] = 0.5

        # Generate signals
        signals = np.full(len(data), 0)
        signals[data > upper_band] = -1  # Overbought
        signals[data < lower_band] = 1  # Oversold

        return IndicatorResult(
            values=sma_values,
            signals=signals,
            metadata={
                "upper_band": upper_band,
                "lower_band": lower_band,
                "middle_band": sma_values,
                "percent_b": percent_b,
                "std_dev": self.std_dev,
            },
        )


class WilliamsR(BaseIndicator):
    """Williams %R."""

    def __init__(self, period: int = 14):
        super().__init__("WilliamsR", period)

    def calculate(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray, **kwargs
    ) -> IndicatorResult:
        """Calculate Williams %R."""
        if not self.validate_data(close, self.period):
            return IndicatorResult(values=np.array([]))

        williams_r = np.full(len(close), np.nan)

        for i in range(self.period - 1, len(close)):
            period_high = np.max(high[i - self.period + 1 : i + 1])
            period_low = np.min(low[i - self.period + 1 : i + 1])

            if period_high != period_low:
                williams_r[i] = (
                    -100 * (period_high - close[i]) / (period_high - period_low)
                )
            else:
                williams_r[i] = -50

        # Generate signals
        signals = np.full(len(close), 0)
        signals[williams_r > -20] = -1  # Overbought
        signals[williams_r < -80] = 1  # Oversold

        return IndicatorResult(
            values=williams_r,
            signals=signals,
            metadata={"overbought": -20, "oversold": -80},
        )


class CCI(BaseIndicator):
    """Commodity Channel Index."""

    def __init__(self, period: int = 20):
        super().__init__("CCI", period)

    def calculate(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray, **kwargs
    ) -> IndicatorResult:
        """Calculate Commodity Channel Index."""
        if not self.validate_data(close, self.period):
            return IndicatorResult(values=np.array([]))

        # Calculate typical price
        typical_price = (high + low + close) / 3

        # Calculate CCI
        cci_values = np.full(len(close), np.nan)

        for i in range(self.period - 1, len(close)):
            period_tp = typical_price[i - self.period + 1 : i + 1]
            sma_tp = np.mean(period_tp)
            mad = np.mean(np.abs(period_tp - sma_tp))

            if mad != 0:
                cci_values[i] = (typical_price[i] - sma_tp) / (0.015 * mad)
            else:
                cci_values[i] = 0

        # Generate signals
        signals = np.full(len(close), 0)
        signals[cci_values > 100] = -1  # Overbought
        signals[cci_values < -100] = 1  # Oversold

        return IndicatorResult(
            values=cci_values,
            signals=signals,
            metadata={"overbought": 100, "oversold": -100},
        )


class ROC(BaseIndicator):
    """Rate of Change."""

    def __init__(self, period: int = 10):
        super().__init__("ROC", period)

    def calculate(self, data: np.ndarray, **kwargs) -> IndicatorResult:
        """Calculate Rate of Change."""
        if not self.validate_data(data, self.period + 1):
            return IndicatorResult(values=np.array([]))

        roc_values = np.full(len(data), np.nan)

        for i in range(self.period, len(data)):
            if data[i - self.period] != 0:
                roc_values[i] = (
                    (data[i] - data[i - self.period]) / data[i - self.period]
                ) * 100

        return IndicatorResult(values=roc_values)


class Momentum(BaseIndicator):
    """Momentum Indicator."""

    def __init__(self, period: int = 10):
        super().__init__("Momentum", period)

    def calculate(self, data: np.ndarray, **kwargs) -> IndicatorResult:
        """Calculate Momentum."""
        if not self.validate_data(data, self.period + 1):
            return IndicatorResult(values=np.array([]))

        momentum_values = np.full(len(data), np.nan)

        for i in range(self.period, len(data)):
            momentum_values[i] = data[i] - data[i - self.period]

        return IndicatorResult(values=momentum_values)
