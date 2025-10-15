"""
Advanced Pattern Recognition
Elliott Wave Theory and Harmonic Pattern Detection
"""

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class WaveType(Enum):
    """Elliott Wave types."""

    IMPULSE = "impulse"
    CORRECTIVE = "corrective"
    EXTENSION = "extension"
    DIAGONAL = "diagonal"


class HarmonicPattern(Enum):
    """Harmonic pattern types."""

    GARTLEY = "gartley"
    BAT = "bat"
    BUTTERFLY = "butterfly"
    CRAB = "crab"
    CYPHER = "cypher"
    SHARK = "shark"


@dataclass
class WavePoint:
    """Elliott Wave point."""

    index: int
    price: float
    timestamp: int
    wave_type: Optional[WaveType] = None
    degree: Optional[int] = None


@dataclass
class ElliottWavePattern:
    """Elliott Wave pattern."""

    waves: List[WavePoint]
    pattern_type: WaveType
    degree: int
    confidence: float
    fibonacci_levels: Dict[str, float]
    metadata: Dict[str, Any]


@dataclass
class HarmonicPatternData:
    """Harmonic pattern data."""

    pattern_type: HarmonicPattern
    points: List[Tuple[int, float]]  # (index, price)
    fibonacci_ratios: Dict[str, float]
    confidence: float
    metadata: Dict[str, Any]


class ElliottWaveDetector:
    """
    Elliott Wave Theory Pattern Detection.

    Implements the core principles of Elliott Wave Theory for identifying
    market cycles and wave patterns.
    """

    def __init__(
        self,
        min_wave_length: int = 5,
        max_wave_length: int = 100,
        fibonacci_tolerance: float = 0.1,
    ):
        """
        Initialize Elliott Wave detector.

        Args:
            min_wave_length: Minimum wave length for detection
            max_wave_length: Maximum wave length for detection
            fibonacci_tolerance: Tolerance for Fibonacci ratio matching
        """
        self.min_wave_length = min_wave_length
        self.max_wave_length = max_wave_length
        self.fibonacci_tolerance = fibonacci_tolerance

        # Key Fibonacci ratios for Elliott Wave analysis
        self.fibonacci_ratios = {
            "0.236": 0.236,
            "0.382": 0.382,
            "0.5": 0.5,
            "0.618": 0.618,
            "0.786": 0.786,
            "1.0": 1.0,
            "1.272": 1.272,
            "1.414": 1.414,
            "1.618": 1.618,
            "2.0": 2.0,
            "2.618": 2.618,
            "3.618": 3.618,
        }

        logger.info(
            f"ElliottWaveDetector initialized: min_length={min_wave_length}, max_length={max_wave_length}"
        )

    def detect_waves(
        self,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        timestamps: Optional[np.ndarray] = None,
    ) -> List[ElliottWavePattern]:
        """
        Detect Elliott Wave patterns.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            timestamps: Optional timestamps

        Returns:
            List of detected Elliott Wave patterns
        """
        if timestamps is None:
            timestamps = np.arange(len(close))

        patterns = []

        # Find significant pivots
        pivots = self._find_pivots(high, low, close)

        # Detect impulse waves
        impulse_patterns = self._detect_impulse_waves(pivots, close, timestamps)
        patterns.extend(impulse_patterns)

        # Detect corrective waves
        corrective_patterns = self._detect_corrective_waves(pivots, close, timestamps)
        patterns.extend(corrective_patterns)

        return patterns

    def _find_pivots(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> List[WavePoint]:
        """Find significant pivot points."""
        pivots = []

        for i in range(2, len(close) - 2):
            # Check for local maxima
            if (
                high[i] > high[i - 1]
                and high[i] > high[i - 2]
                and high[i] > high[i + 1]
                and high[i] > high[i + 2]
            ):
                pivots.append(
                    WavePoint(
                        index=i, price=high[i], timestamp=i, wave_type=WaveType.IMPULSE
                    )
                )

            # Check for local minima
            elif (
                low[i] < low[i - 1]
                and low[i] < low[i - 2]
                and low[i] < low[i + 1]
                and low[i] < low[i + 2]
            ):
                pivots.append(
                    WavePoint(
                        index=i,
                        price=low[i],
                        timestamp=i,
                        wave_type=WaveType.CORRECTIVE,
                    )
                )

        return pivots

    def _detect_impulse_waves(
        self, pivots: List[WavePoint], close: np.ndarray, timestamps: np.ndarray
    ) -> List[ElliottWavePattern]:
        """Detect impulse wave patterns (5-wave structure)."""
        patterns = []

        for i in range(len(pivots) - 4):
            # Check for 5-wave impulse pattern
            wave_points = pivots[i : i + 5]

            if self._is_valid_impulse_pattern(wave_points):
                fibonacci_levels = self._calculate_fibonacci_levels(wave_points)
                confidence = self._calculate_impulse_confidence(
                    wave_points, fibonacci_levels
                )

                if confidence > 0.6:
                    patterns.append(
                        ElliottWavePattern(
                            waves=wave_points,
                            pattern_type=WaveType.IMPULSE,
                            degree=1,
                            confidence=confidence,
                            fibonacci_levels=fibonacci_levels,
                            metadata={
                                "wave_count": 5,
                                "direction": (
                                    "bullish"
                                    if wave_points[-1].price > wave_points[0].price
                                    else "bearish"
                                ),
                            },
                        )
                    )

        return patterns

    def _detect_corrective_waves(
        self, pivots: List[WavePoint], close: np.ndarray, timestamps: np.ndarray
    ) -> List[ElliottWavePattern]:
        """Detect corrective wave patterns (3-wave structure)."""
        patterns = []

        for i in range(len(pivots) - 2):
            # Check for 3-wave corrective pattern
            wave_points = pivots[i : i + 3]

            if self._is_valid_corrective_pattern(wave_points):
                fibonacci_levels = self._calculate_fibonacci_levels(wave_points)
                confidence = self._calculate_corrective_confidence(
                    wave_points, fibonacci_levels
                )

                if confidence > 0.6:
                    patterns.append(
                        ElliottWavePattern(
                            waves=wave_points,
                            pattern_type=WaveType.CORRECTIVE,
                            degree=1,
                            confidence=confidence,
                            fibonacci_levels=fibonacci_levels,
                            metadata={
                                "wave_count": 3,
                                "direction": (
                                    "bullish"
                                    if wave_points[-1].price > wave_points[0].price
                                    else "bearish"
                                ),
                            },
                        )
                    )

        return patterns

    def _is_valid_impulse_pattern(self, wave_points: List[WavePoint]) -> bool:
        """Check if wave points form a valid impulse pattern."""
        if len(wave_points) != 5:
            return False

        # Check wave relationships
        wave1 = wave_points[1].price - wave_points[0].price
        wave2 = wave_points[2].price - wave_points[1].price
        wave3 = wave_points[3].price - wave_points[2].price
        wave4 = wave_points[4].price - wave_points[3].price

        # Wave 3 should be the longest
        if abs(wave3) <= abs(wave1) or abs(wave3) <= abs(wave4):
            return False

        # Wave 2 should not retrace more than 100% of wave 1
        if abs(wave2) > abs(wave1):
            return False

        # Wave 4 should not overlap with wave 1
        if (
            wave_points[3].price > wave_points[1].price
            and wave_points[4].price < wave_points[2].price
        ):
            return False

        return True

    def _is_valid_corrective_pattern(self, wave_points: List[WavePoint]) -> bool:
        """Check if wave points form a valid corrective pattern."""
        if len(wave_points) != 3:
            return False

        # Check wave relationships
        wave_a = wave_points[1].price - wave_points[0].price
        wave_b = wave_points[2].price - wave_points[1].price

        # Wave B should retrace part of wave A
        if abs(wave_b) > abs(wave_a):
            return False

        return True

    def _calculate_fibonacci_levels(
        self, wave_points: List[WavePoint]
    ) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels."""
        if len(wave_points) < 2:
            return {}

        start_price = wave_points[0].price
        end_price = wave_points[-1].price
        price_range = end_price - start_price

        fibonacci_levels = {}
        for name, ratio in self.fibonacci_ratios.items():
            fibonacci_levels[name] = start_price + (price_range * ratio)

        return fibonacci_levels

    def _calculate_impulse_confidence(
        self, wave_points: List[WavePoint], fibonacci_levels: Dict[str, float]
    ) -> float:
        """Calculate confidence score for impulse pattern."""
        confidence = 0.0

        # Wave relationship factor
        wave1 = wave_points[1].price - wave_points[0].price
        wave3 = wave_points[3].price - wave_points[2].price
        wave5 = wave_points[4].price - wave_points[3].price

        # Wave 3 should be 1.618 times wave 1
        if abs(wave1) > 0:
            ratio_13 = abs(wave3) / abs(wave1)
            if 1.4 <= ratio_13 <= 2.0:
                confidence += 0.3

        # Wave 5 should be 0.618 times wave 1
        if abs(wave1) > 0:
            ratio_15 = abs(wave5) / abs(wave1)
            if 0.4 <= ratio_15 <= 0.8:
                confidence += 0.3

        # Fibonacci level factor
        confidence += 0.2

        # Pattern completeness factor
        confidence += 0.2

        return min(confidence, 1.0)

    def _calculate_corrective_confidence(
        self, wave_points: List[WavePoint], fibonacci_levels: Dict[str, float]
    ) -> float:
        """Calculate confidence score for corrective pattern."""
        confidence = 0.0

        # Wave relationship factor
        wave_a = wave_points[1].price - wave_points[0].price
        wave_b = wave_points[2].price - wave_points[1].price

        # Wave B should retrace 0.618 of wave A
        if abs(wave_a) > 0:
            ratio_ab = abs(wave_b) / abs(wave_a)
            if 0.5 <= ratio_ab <= 0.8:
                confidence += 0.4

        # Fibonacci level factor
        confidence += 0.3

        # Pattern completeness factor
        confidence += 0.3

        return min(confidence, 1.0)


class HarmonicPatternDetector:
    """
    Harmonic Pattern Detection.

    Implements detection of harmonic patterns like Gartley, Bat, Butterfly, etc.
    """

    def __init__(
        self, fibonacci_tolerance: float = 0.05, min_pattern_size: float = 0.5
    ):
        """
        Initialize harmonic pattern detector.

        Args:
            fibonacci_tolerance: Tolerance for Fibonacci ratio matching
            min_pattern_size: Minimum pattern size (percentage)
        """
        self.fibonacci_tolerance = fibonacci_tolerance
        self.min_pattern_size = min_pattern_size

        # Harmonic pattern definitions
        self.pattern_definitions = {
            HarmonicPattern.GARTLEY: {"AB": 0.618, "BC": 0.382, "CD": 1.272},
            HarmonicPattern.BAT: {"AB": 0.382, "BC": 0.382, "CD": 1.618},
            HarmonicPattern.BUTTERFLY: {"AB": 0.786, "BC": 0.382, "CD": 1.618},
            HarmonicPattern.CRAB: {"AB": 0.382, "BC": 0.382, "CD": 2.618},
            HarmonicPattern.CYPHER: {"AB": 0.382, "BC": 1.13, "CD": 1.414},
            HarmonicPattern.SHARK: {"AB": 0.382, "BC": 0.382, "CD": 1.618},
        }

        logger.info(
            f"HarmonicPatternDetector initialized: tolerance={fibonacci_tolerance}"
        )

    def detect_harmonic_patterns(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> List[HarmonicPatternData]:
        """
        Detect harmonic patterns.

        Args:
            high: High prices
            low: Low prices
            close: Close prices

        Returns:
            List of detected harmonic patterns
        """
        patterns = []

        # Find significant pivots
        pivots = self._find_significant_pivots(high, low, close)

        # Check for each harmonic pattern
        for pattern_type in HarmonicPattern:
            detected_patterns = self._detect_pattern(
                pattern_type, pivots, high, low, close
            )
            patterns.extend(detected_patterns)

        return patterns

    def _find_significant_pivots(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> List[Tuple[int, float, str]]:
        """Find significant pivot points."""
        pivots = []

        for i in range(5, len(close) - 5):
            # Check for local maxima
            if high[i] > np.max(high[i - 5 : i]) and high[i] > np.max(
                high[i + 1 : i + 6]
            ):
                pivots.append((i, high[i], "high"))

            # Check for local minima
            elif low[i] < np.min(low[i - 5 : i]) and low[i] < np.min(
                low[i + 1 : i + 6]
            ):
                pivots.append((i, low[i], "low"))

        return pivots

    def _detect_pattern(
        self,
        pattern_type: HarmonicPattern,
        pivots: List[Tuple[int, float, str]],
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
    ) -> List[HarmonicPatternData]:
        """Detect specific harmonic pattern."""
        patterns = []
        pattern_def = self.pattern_definitions[pattern_type]

        for i in range(len(pivots) - 3):
            # Get 4 pivot points for harmonic pattern
            point_a = pivots[i]
            point_b = pivots[i + 1]
            point_c = pivots[i + 2]
            point_d = pivots[i + 3]

            # Check if points form valid pattern
            if self._is_valid_harmonic_pattern(
                point_a, point_b, point_c, point_d, pattern_def
            ):
                fibonacci_ratios = self._calculate_harmonic_ratios(
                    point_a, point_b, point_c, point_d
                )
                confidence = self._calculate_harmonic_confidence(
                    fibonacci_ratios, pattern_def
                )

                if confidence > 0.7:
                    patterns.append(
                        HarmonicPatternData(
                            pattern_type=pattern_type,
                            points=[point_a, point_b, point_c, point_d],
                            fibonacci_ratios=fibonacci_ratios,
                            confidence=confidence,
                            metadata={
                                "pattern_name": pattern_type.value,
                                "point_count": 4,
                            },
                        )
                    )

        return patterns

    def _is_valid_harmonic_pattern(
        self,
        point_a: Tuple[int, float, str],
        point_b: Tuple[int, float, str],
        point_c: Tuple[int, float, str],
        point_d: Tuple[int, float, str],
        pattern_def: Dict[str, float],
    ) -> bool:
        """Check if points form valid harmonic pattern."""
        # Check alternating pivot types
        if (
            point_a[2] == point_b[2]
            or point_b[2] == point_c[2]
            or point_c[2] == point_d[2]
        ):
            return False

        # Check pattern size
        price_range = abs(point_d[1] - point_a[1])
        if price_range < self.min_pattern_size:
            return False

        return True

    def _calculate_harmonic_ratios(
        self,
        point_a: Tuple[int, float, str],
        point_b: Tuple[int, float, str],
        point_c: Tuple[int, float, str],
        point_d: Tuple[int, float, str],
    ) -> Dict[str, float]:
        """Calculate Fibonacci ratios for harmonic pattern."""
        ratios = {}

        # Calculate AB ratio
        ab_range = abs(point_b[1] - point_a[1])
        bc_range = abs(point_c[1] - point_b[1])
        cd_range = abs(point_d[1] - point_c[1])

        if ab_range > 0:
            ratios["AB"] = bc_range / ab_range
        if bc_range > 0:
            ratios["BC"] = cd_range / bc_range
        if ab_range > 0:
            ratios["CD"] = cd_range / ab_range

        return ratios

    def _calculate_harmonic_confidence(
        self, fibonacci_ratios: Dict[str, float], pattern_def: Dict[str, float]
    ) -> float:
        """Calculate confidence score for harmonic pattern."""
        confidence = 0.0

        for ratio_name, expected_ratio in pattern_def.items():
            if ratio_name in fibonacci_ratios:
                actual_ratio = fibonacci_ratios[ratio_name]
                error = abs(actual_ratio - expected_ratio) / expected_ratio

                if error <= self.fibonacci_tolerance:
                    confidence += 1.0
                elif error <= self.fibonacci_tolerance * 2:
                    confidence += 0.5

        # Normalize confidence
        if len(pattern_def) > 0:
            confidence /= len(pattern_def)

        return confidence


class CandlestickPatternDetector:
    """
    Candlestick Pattern Recognition.

    Implements detection of common candlestick patterns.
    """

    def __init__(self):
        """Initialize candlestick pattern detector."""
        self.patterns = {
            "doji": self._detect_doji,
            "hammer": self._detect_hammer,
            "shooting_star": self._detect_shooting_star,
            "engulfing": self._detect_engulfing,
            "harami": self._detect_harami,
            "morning_star": self._detect_morning_star,
            "evening_star": self._detect_evening_star,
        }

        logger.info("CandlestickPatternDetector initialized")

    def detect_patterns(
        self,
        open_prices: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
    ) -> Dict[str, List[Tuple[int, float]]]:
        """
        Detect candlestick patterns.

        Args:
            open_prices: Open prices
            high: High prices
            low: Low prices
            close: Close prices

        Returns:
            Dictionary of detected patterns with indices and confidence
        """
        results = {}

        for pattern_name, detector_func in self.patterns.items():
            results[pattern_name] = detector_func(open_prices, high, low, close)

        return results

    def _detect_doji(
        self,
        open_prices: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
    ) -> List[Tuple[int, float]]:
        """Detect Doji patterns."""
        patterns = []

        for i in range(len(close)):
            body_size = abs(close[i] - open_prices[i])
            total_range = high[i] - low[i]

            if total_range > 0 and body_size / total_range < 0.1:
                patterns.append((i, 0.8))

        return patterns

    def _detect_hammer(
        self,
        open_prices: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
    ) -> List[Tuple[int, float]]:
        """Detect Hammer patterns."""
        patterns = []

        for i in range(len(close)):
            body_size = abs(close[i] - open_prices[i])
            total_range = high[i] - low[i]
            lower_shadow = min(open_prices[i], close[i]) - low[i]
            upper_shadow = high[i] - max(open_prices[i], close[i])

            if (
                total_range > 0
                and body_size / total_range < 0.3
                and lower_shadow > body_size * 2
                and upper_shadow < body_size
            ):
                patterns.append((i, 0.7))

        return patterns

    def _detect_shooting_star(
        self,
        open_prices: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
    ) -> List[Tuple[int, float]]:
        """Detect Shooting Star patterns."""
        patterns = []

        for i in range(len(close)):
            body_size = abs(close[i] - open_prices[i])
            total_range = high[i] - low[i]
            lower_shadow = min(open_prices[i], close[i]) - low[i]
            upper_shadow = high[i] - max(open_prices[i], close[i])

            if (
                total_range > 0
                and body_size / total_range < 0.3
                and upper_shadow > body_size * 2
                and lower_shadow < body_size
            ):
                patterns.append((i, 0.7))

        return patterns

    def _detect_engulfing(
        self,
        open_prices: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
    ) -> List[Tuple[int, float]]:
        """Detect Engulfing patterns."""
        patterns = []

        for i in range(1, len(close)):
            prev_body = abs(close[i - 1] - open_prices[i - 1])
            curr_body = abs(close[i] - open_prices[i])

            # Bullish engulfing
            if (
                close[i - 1] < open_prices[i - 1]
                and close[i] > open_prices[i]
                and close[i] > open_prices[i - 1]
                and open_prices[i] < close[i - 1]
            ):
                patterns.append((i, 0.8))

            # Bearish engulfing
            elif (
                close[i - 1] > open_prices[i - 1]
                and close[i] < open_prices[i]
                and close[i] < open_prices[i - 1]
                and open_prices[i] > close[i - 1]
            ):
                patterns.append((i, 0.8))

        return patterns

    def _detect_harami(
        self,
        open_prices: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
    ) -> List[Tuple[int, float]]:
        """Detect Harami patterns."""
        patterns = []

        for i in range(1, len(close)):
            prev_body = abs(close[i - 1] - open_prices[i - 1])
            curr_body = abs(close[i] - open_prices[i])

            # Harami pattern
            if (
                prev_body > curr_body * 2
                and max(open_prices[i], close[i])
                < max(open_prices[i - 1], close[i - 1])
                and min(open_prices[i], close[i])
                > min(open_prices[i - 1], close[i - 1])
            ):
                patterns.append((i, 0.6))

        return patterns

    def _detect_morning_star(
        self,
        open_prices: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
    ) -> List[Tuple[int, float]]:
        """Detect Morning Star patterns."""
        patterns = []

        for i in range(2, len(close)):
            # First candle: bearish
            if close[i - 2] < open_prices[i - 2]:
                # Second candle: small body (star)
                star_body = abs(close[i - 1] - open_prices[i - 1])
                first_body = abs(close[i - 2] - open_prices[i - 2])

                if star_body < first_body * 0.3:
                    # Third candle: bullish
                    if (
                        close[i] > open_prices[i]
                        and close[i] > (open_prices[i - 2] + close[i - 2]) / 2
                    ):
                        patterns.append((i, 0.8))

        return patterns

    def _detect_evening_star(
        self,
        open_prices: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
    ) -> List[Tuple[int, float]]:
        """Detect Evening Star patterns."""
        patterns = []

        for i in range(2, len(close)):
            # First candle: bullish
            if close[i - 2] > open_prices[i - 2]:
                # Second candle: small body (star)
                star_body = abs(close[i - 1] - open_prices[i - 1])
                first_body = abs(close[i - 2] - open_prices[i - 2])

                if star_body < first_body * 0.3:
                    # Third candle: bearish
                    if (
                        close[i] < open_prices[i]
                        and close[i] < (open_prices[i - 2] + close[i - 2]) / 2
                    ):
                        patterns.append((i, 0.8))

        return patterns


class PatternAnalyzer:
    """
    Comprehensive Pattern Analysis.

    Combines all pattern detectors to provide complete analysis.
    """

    def __init__(self):
        """Initialize pattern analyzer."""
        self.elliott_detector = ElliottWaveDetector()
        self.harmonic_detector = HarmonicPatternDetector()
        self.candlestick_detector = CandlestickPatternDetector()

        logger.info("PatternAnalyzer initialized with all detectors")

    def analyze_patterns(
        self,
        open_prices: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray,
        timestamps: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive pattern analysis.

        Args:
            open_prices: Open prices
            high: High prices
            low: Low prices
            close: Close prices
            volume: Volume data
            timestamps: Optional timestamps

        Returns:
            Dictionary of all detected patterns
        """
        results = {}

        # Elliott Wave analysis
        results["elliott_waves"] = self.elliott_detector.detect_waves(
            high, low, close, timestamps
        )

        # Harmonic pattern analysis
        results["harmonic_patterns"] = self.harmonic_detector.detect_harmonic_patterns(
            high, low, close
        )

        # Candlestick pattern analysis
        results["candlestick_patterns"] = self.candlestick_detector.detect_patterns(
            open_prices, high, low, close
        )

        return results

    def get_pattern_features(
        self,
        open_prices: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray,
    ) -> np.ndarray:
        """
        Extract pattern features for machine learning.

        Args:
            open_prices: Open prices
            high: High prices
            low: Low prices
            close: Close prices
            volume: Volume data

        Returns:
            Feature array
        """
        features = []

        # Analyze patterns
        pattern_results = self.analyze_patterns(open_prices, high, low, close, volume)

        # Extract features
        for i in range(len(close)):
            feature_vector = []

            # Elliott Wave features
            ew_count = sum(
                1
                for pattern in pattern_results["elliott_waves"]
                if any(wave.index == i for wave in pattern.waves)
            )
            feature_vector.append(ew_count)

            # Harmonic pattern features
            hp_count = sum(
                1
                for pattern in pattern_results["harmonic_patterns"]
                if any(point[0] == i for point in pattern.points)
            )
            feature_vector.append(hp_count)

            # Candlestick pattern features
            cs_count = sum(
                1
                for pattern_list in pattern_results["candlestick_patterns"].values()
                if any(idx == i for idx, _ in pattern_list)
            )
            feature_vector.append(cs_count)

            features.append(feature_vector)

        return np.array(features)
