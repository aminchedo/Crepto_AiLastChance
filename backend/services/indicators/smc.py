"""
Smart Money Concepts (SMC) Indicators
Implementation of institutional trading concepts
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class SMCType(Enum):
    """Types of Smart Money Concepts."""

    ORDER_BLOCK = "order_block"
    FAIR_VALUE_GAP = "fair_value_gap"
    BREAK_OF_STRUCTURE = "break_of_structure"
    LIQUIDITY_ZONE = "liquidity_zone"
    SWEEP = "sweep"
    MITIGATION = "mitigation"


@dataclass
class SMCPattern:
    """Smart Money Concept pattern."""

    pattern_type: SMCType
    start_index: int
    end_index: int
    high: float
    low: float
    confidence: float
    metadata: Dict[str, Any]


class OrderBlockDetector:
    """
    Order Block Detection for Smart Money Concepts.

    Order Blocks are areas where institutional traders placed large orders.
    They represent significant support/resistance levels.
    """

    def __init__(
        self,
        min_block_size: float = 0.5,
        min_volume_ratio: float = 1.5,
        confirmation_candles: int = 3,
    ):
        """
        Initialize Order Block detector.

        Args:
            min_block_size: Minimum size for order block (percentage)
            min_volume_ratio: Minimum volume ratio for confirmation
            confirmation_candles: Number of candles for confirmation
        """
        self.min_block_size = min_block_size
        self.min_volume_ratio = min_volume_ratio
        self.confirmation_candles = confirmation_candles

        logger.info(
            f"OrderBlockDetector initialized: min_size={min_block_size}, min_volume_ratio={min_volume_ratio}"
        )

    def detect_bullish_order_blocks(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray
    ) -> List[SMCPattern]:
        """
        Detect bullish order blocks.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            volume: Volume data

        Returns:
            List of detected bullish order blocks
        """
        order_blocks = []

        for i in range(
            self.confirmation_candles, len(close) - self.confirmation_candles
        ):
            # Look for strong bullish candle
            if self._is_strong_bullish_candle(i, high, low, close, volume):
                # Check if it's followed by consolidation
                if self._is_consolidation(i, high, low, close, volume):
                    # Calculate order block parameters
                    block_high = high[i]
                    block_low = low[i]
                    block_size = (block_high - block_low) / block_low

                    if block_size >= self.min_block_size:
                        # Calculate confidence
                        confidence = self._calculate_order_block_confidence(
                            i, high, low, close, volume, True
                        )

                        if confidence > 0.6:
                            order_blocks.append(
                                SMCPattern(
                                    pattern_type=SMCType.ORDER_BLOCK,
                                    start_index=i,
                                    end_index=i + self.confirmation_candles,
                                    high=block_high,
                                    low=block_low,
                                    confidence=confidence,
                                    metadata={
                                        "direction": "bullish",
                                        "block_size": block_size,
                                        "volume_ratio": volume[i]
                                        / np.mean(volume[max(0, i - 10) : i]),
                                        "confirmation_candles": self.confirmation_candles,
                                    },
                                )
                            )

        return order_blocks

    def detect_bearish_order_blocks(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray
    ) -> List[SMCPattern]:
        """
        Detect bearish order blocks.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            volume: Volume data

        Returns:
            List of detected bearish order blocks
        """
        order_blocks = []

        for i in range(
            self.confirmation_candles, len(close) - self.confirmation_candles
        ):
            # Look for strong bearish candle
            if self._is_strong_bearish_candle(i, high, low, close, volume):
                # Check if it's followed by consolidation
                if self._is_consolidation(i, high, low, close, volume):
                    # Calculate order block parameters
                    block_high = high[i]
                    block_low = low[i]
                    block_size = (block_high - block_low) / block_high

                    if block_size >= self.min_block_size:
                        # Calculate confidence
                        confidence = self._calculate_order_block_confidence(
                            i, high, low, close, volume, False
                        )

                        if confidence > 0.6:
                            order_blocks.append(
                                SMCPattern(
                                    pattern_type=SMCType.ORDER_BLOCK,
                                    start_index=i,
                                    end_index=i + self.confirmation_candles,
                                    high=block_high,
                                    low=block_low,
                                    confidence=confidence,
                                    metadata={
                                        "direction": "bearish",
                                        "block_size": block_size,
                                        "volume_ratio": volume[i]
                                        / np.mean(volume[max(0, i - 10) : i]),
                                        "confirmation_candles": self.confirmation_candles,
                                    },
                                )
                            )

        return order_blocks

    def _is_strong_bullish_candle(
        self,
        index: int,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray,
    ) -> bool:
        """Check if candle is a strong bullish candle."""
        candle_range = high[index] - low[index]
        body_size = close[index] - low[index]

        # Strong bullish candle: large body, small wick
        body_ratio = body_size / candle_range if candle_range > 0 else 0

        # High volume
        avg_volume = np.mean(volume[max(0, index - 10) : index])
        volume_ratio = volume[index] / avg_volume if avg_volume > 0 else 0

        return body_ratio > 0.7 and volume_ratio > self.min_volume_ratio

    def _is_strong_bearish_candle(
        self,
        index: int,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray,
    ) -> bool:
        """Check if candle is a strong bearish candle."""
        candle_range = high[index] - low[index]
        body_size = high[index] - close[index]

        # Strong bearish candle: large body, small wick
        body_ratio = body_size / candle_range if candle_range > 0 else 0

        # High volume
        avg_volume = np.mean(volume[max(0, index - 10) : index])
        volume_ratio = volume[index] / avg_volume if avg_volume > 0 else 0

        return body_ratio > 0.7 and volume_ratio > self.min_volume_ratio

    def _is_consolidation(
        self,
        start_index: int,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray,
    ) -> bool:
        """Check if there's consolidation after the strong candle."""
        if start_index + self.confirmation_candles >= len(close):
            return False

        # Check if price stays within the range of the strong candle
        strong_candle_high = high[start_index]
        strong_candle_low = low[start_index]

        for i in range(start_index + 1, start_index + self.confirmation_candles + 1):
            if high[i] > strong_candle_high or low[i] < strong_candle_low:
                return False

        return True

    def _calculate_order_block_confidence(
        self,
        index: int,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray,
        is_bullish: bool,
    ) -> float:
        """Calculate confidence score for order block."""
        confidence = 0.0

        # Volume factor
        avg_volume = np.mean(volume[max(0, index - 10) : index])
        volume_ratio = volume[index] / avg_volume if avg_volume > 0 else 0
        confidence += min(volume_ratio / 3.0, 0.3)

        # Price action factor
        candle_range = high[index] - low[index]
        if is_bullish:
            body_size = close[index] - low[index]
        else:
            body_size = high[index] - close[index]

        body_ratio = body_size / candle_range if candle_range > 0 else 0
        confidence += min(body_ratio, 0.3)

        # Consolidation factor
        if self._is_consolidation(index, high, low, close, volume):
            confidence += 0.2

        # Trend factor
        if index >= 20:
            recent_trend = np.mean(close[index - 20 : index]) - np.mean(
                close[index - 40 : index - 20]
            )
            if is_bullish and recent_trend > 0:
                confidence += 0.1
            elif not is_bullish and recent_trend < 0:
                confidence += 0.1

        return min(confidence, 1.0)


class FairValueGapDetector:
    """
    Fair Value Gap (FVG) Detection.

    FVGs are gaps between candles that represent areas where price
    moved too quickly, leaving a "fair value" gap to be filled.
    """

    def __init__(
        self,
        min_gap_size: float = 0.2,
        max_gap_size: float = 5.0,
        fill_threshold: float = 0.8,
    ):
        """
        Initialize FVG detector.

        Args:
            min_gap_size: Minimum gap size (percentage)
            max_gap_size: Maximum gap size (percentage)
            fill_threshold: Threshold for considering gap filled
        """
        self.min_gap_size = min_gap_size
        self.max_gap_size = max_gap_size
        self.fill_threshold = fill_threshold

        logger.info(
            f"FairValueGapDetector initialized: min_gap={min_gap_size}, max_gap={max_gap_size}"
        )

    def detect_fair_value_gaps(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> List[SMCPattern]:
        """
        Detect Fair Value Gaps.

        Args:
            high: High prices
            low: Low prices
            close: Close prices

        Returns:
            List of detected FVGs
        """
        fvgs = []

        for i in range(2, len(close) - 1):
            # Check for bullish FVG (gap between candle 1 low and candle 3 high)
            if self._is_bullish_fvg(i, high, low, close):
                gap_low = low[i - 1]
                gap_high = high[i + 1]
                gap_size = (gap_high - gap_low) / gap_low

                if self.min_gap_size <= gap_size <= self.max_gap_size:
                    confidence = self._calculate_fvg_confidence(
                        i, high, low, close, True
                    )

                    fvgs.append(
                        SMCPattern(
                            pattern_type=SMCType.FAIR_VALUE_GAP,
                            start_index=i - 1,
                            end_index=i + 1,
                            high=gap_high,
                            low=gap_low,
                            confidence=confidence,
                            metadata={
                                "direction": "bullish",
                                "gap_size": gap_size,
                                "fill_threshold": self.fill_threshold,
                            },
                        )
                    )

            # Check for bearish FVG (gap between candle 1 high and candle 3 low)
            elif self._is_bearish_fvg(i, high, low, close):
                gap_high = high[i - 1]
                gap_low = low[i + 1]
                gap_size = (gap_high - gap_low) / gap_high

                if self.min_gap_size <= gap_size <= self.max_gap_size:
                    confidence = self._calculate_fvg_confidence(
                        i, high, low, close, False
                    )

                    fvgs.append(
                        SMCPattern(
                            pattern_type=SMCType.FAIR_VALUE_GAP,
                            start_index=i - 1,
                            end_index=i + 1,
                            high=gap_high,
                            low=gap_low,
                            confidence=confidence,
                            metadata={
                                "direction": "bearish",
                                "gap_size": gap_size,
                                "fill_threshold": self.fill_threshold,
                            },
                        )
                    )

        return fvgs

    def _is_bullish_fvg(
        self, index: int, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> bool:
        """Check if there's a bullish FVG at index."""
        # Candle 1: strong bullish
        candle1_bullish = close[index - 1] > close[index - 2]

        # Candle 2: gap candle (no overlap)
        gap_exists = low[index] > high[index - 1]

        # Candle 3: strong bearish
        candle3_bearish = close[index + 1] < close[index]

        return candle1_bullish and gap_exists and candle3_bearish

    def _is_bearish_fvg(
        self, index: int, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> bool:
        """Check if there's a bearish FVG at index."""
        # Candle 1: strong bearish
        candle1_bearish = close[index - 1] < close[index - 2]

        # Candle 2: gap candle (no overlap)
        gap_exists = high[index] < low[index - 1]

        # Candle 3: strong bullish
        candle3_bullish = close[index + 1] > close[index]

        return candle1_bearish and gap_exists and candle3_bullish

    def _calculate_fvg_confidence(
        self,
        index: int,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        is_bullish: bool,
    ) -> float:
        """Calculate confidence score for FVG."""
        confidence = 0.0

        # Gap size factor
        if is_bullish:
            gap_size = (high[index + 1] - low[index - 1]) / low[index - 1]
        else:
            gap_size = (high[index - 1] - low[index + 1]) / high[index - 1]

        # Optimal gap size gets higher confidence
        if 0.5 <= gap_size <= 2.0:
            confidence += 0.4
        elif 0.2 <= gap_size <= 5.0:
            confidence += 0.2

        # Volume factor (if available)
        # This would require volume data

        # Trend factor
        if index >= 20:
            recent_trend = np.mean(close[index - 20 : index]) - np.mean(
                close[index - 40 : index - 20]
            )
            if is_bullish and recent_trend > 0:
                confidence += 0.3
            elif not is_bullish and recent_trend < 0:
                confidence += 0.3

        # Pattern factor
        confidence += 0.3  # Base confidence for valid pattern

        return min(confidence, 1.0)


class BreakOfStructureDetector:
    """
    Break of Structure (BOS) Detection.

    BOS occurs when price breaks a significant high or low,
    indicating a change in market structure.
    """

    def __init__(
        self,
        lookback_period: int = 20,
        min_break_size: float = 0.5,
        confirmation_candles: int = 2,
    ):
        """
        Initialize BOS detector.

        Args:
            lookback_period: Period to look back for structure
            min_break_size: Minimum break size (percentage)
            confirmation_candles: Candles for confirmation
        """
        self.lookback_period = lookback_period
        self.min_break_size = min_break_size
        self.confirmation_candles = confirmation_candles

        logger.info(
            f"BreakOfStructureDetector initialized: lookback={lookback_period}, min_break={min_break_size}"
        )

    def detect_break_of_structure(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> List[SMCPattern]:
        """
        Detect Break of Structure.

        Args:
            high: High prices
            low: Low prices
            close: Close prices

        Returns:
            List of detected BOS patterns
        """
        bos_patterns = []

        for i in range(self.lookback_period, len(close) - self.confirmation_candles):
            # Check for bullish BOS
            if self._is_bullish_bos(i, high, low, close):
                confidence = self._calculate_bos_confidence(i, high, low, close, True)

                bos_patterns.append(
                    SMCPattern(
                        pattern_type=SMCType.BREAK_OF_STRUCTURE,
                        start_index=i,
                        end_index=i + self.confirmation_candles,
                        high=high[i],
                        low=low[i],
                        confidence=confidence,
                        metadata={
                            "direction": "bullish",
                            "break_level": high[i],
                            "lookback_period": self.lookback_period,
                        },
                    )
                )

            # Check for bearish BOS
            elif self._is_bearish_bos(i, high, low, close):
                confidence = self._calculate_bos_confidence(i, high, low, close, False)

                bos_patterns.append(
                    SMCPattern(
                        pattern_type=SMCType.BREAK_OF_STRUCTURE,
                        start_index=i,
                        end_index=i + self.confirmation_candles,
                        high=high[i],
                        low=low[i],
                        confidence=confidence,
                        metadata={
                            "direction": "bearish",
                            "break_level": low[i],
                            "lookback_period": self.lookback_period,
                        },
                    )
                )

        return bos_patterns

    def _is_bullish_bos(
        self, index: int, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> bool:
        """Check if there's a bullish BOS at index."""
        # Find previous high in lookback period
        prev_high = np.max(high[index - self.lookback_period : index])

        # Current candle breaks above previous high
        if high[index] > prev_high:
            # Check for confirmation
            for i in range(1, self.confirmation_candles + 1):
                if index + i < len(close):
                    if close[index + i] < prev_high:
                        return False
            return True

        return False

    def _is_bearish_bos(
        self, index: int, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> bool:
        """Check if there's a bearish BOS at index."""
        # Find previous low in lookback period
        prev_low = np.min(low[index - self.lookback_period : index])

        # Current candle breaks below previous low
        if low[index] < prev_low:
            # Check for confirmation
            for i in range(1, self.confirmation_candles + 1):
                if index + i < len(close):
                    if close[index + i] > prev_low:
                        return False
            return True

        return False

    def _calculate_bos_confidence(
        self,
        index: int,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        is_bullish: bool,
    ) -> float:
        """Calculate confidence score for BOS."""
        confidence = 0.0

        # Break size factor
        if is_bullish:
            prev_high = np.max(high[index - self.lookback_period : index])
            break_size = (high[index] - prev_high) / prev_high
        else:
            prev_low = np.min(low[index - self.lookback_period : index])
            break_size = (prev_low - low[index]) / prev_low

        if break_size >= self.min_break_size:
            confidence += min(break_size / 2.0, 0.4)

        # Volume factor (if available)
        # This would require volume data

        # Trend factor
        if index >= 20:
            recent_trend = np.mean(close[index - 20 : index]) - np.mean(
                close[index - 40 : index - 20]
            )
            if is_bullish and recent_trend > 0:
                confidence += 0.3
            elif not is_bullish and recent_trend < 0:
                confidence += 0.3

        # Confirmation factor
        confidence += 0.3  # Base confidence for valid pattern

        return min(confidence, 1.0)


class LiquidityZoneDetector:
    """
    Liquidity Zone Detection.

    Liquidity zones are areas where stop losses are likely to be placed,
    creating pools of liquidity that institutions can target.
    """

    def __init__(
        self,
        min_zone_size: float = 0.3,
        max_zone_size: float = 3.0,
        min_touches: int = 2,
    ):
        """
        Initialize liquidity zone detector.

        Args:
            min_zone_size: Minimum zone size (percentage)
            max_zone_size: Maximum zone size (percentage)
            min_touches: Minimum number of touches
        """
        self.min_zone_size = min_zone_size
        self.max_zone_size = max_zone_size
        self.min_touches = min_touches

        logger.info(
            f"LiquidityZoneDetector initialized: min_size={min_zone_size}, min_touches={min_touches}"
        )

    def detect_liquidity_zones(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> List[SMCPattern]:
        """
        Detect liquidity zones.

        Args:
            high: High prices
            low: Low prices
            close: Close prices

        Returns:
            List of detected liquidity zones
        """
        liquidity_zones = []

        # Find significant highs and lows
        significant_highs = self._find_significant_highs(high, low, close)
        significant_lows = self._find_significant_lows(high, low, close)

        # Create liquidity zones around significant levels
        for level in significant_highs:
            zone = self._create_liquidity_zone(level, "resistance", high, low, close)
            if zone:
                liquidity_zones.append(zone)

        for level in significant_lows:
            zone = self._create_liquidity_zone(level, "support", high, low, close)
            if zone:
                liquidity_zones.append(zone)

        return liquidity_zones

    def _find_significant_highs(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> List[float]:
        """Find significant highs."""
        significant_highs = []

        for i in range(5, len(high) - 5):
            # Check if current high is higher than surrounding highs
            if high[i] > np.max(high[i - 5 : i]) and high[i] > np.max(
                high[i + 1 : i + 6]
            ):
                significant_highs.append(high[i])

        return significant_highs

    def _find_significant_lows(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> List[float]:
        """Find significant lows."""
        significant_lows = []

        for i in range(5, len(low) - 5):
            # Check if current low is lower than surrounding lows
            if low[i] < np.min(low[i - 5 : i]) and low[i] < np.min(low[i + 1 : i + 6]):
                significant_lows.append(low[i])

        return significant_lows

    def _create_liquidity_zone(
        self,
        level: float,
        zone_type: str,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
    ) -> Optional[SMCPattern]:
        """Create liquidity zone around a level."""
        # Calculate zone boundaries
        zone_size = level * 0.01  # 1% of level

        if zone_type == "resistance":
            zone_high = level + zone_size
            zone_low = level - zone_size
        else:
            zone_high = level + zone_size
            zone_low = level - zone_size

        # Count touches
        touches = 0
        for i in range(len(close)):
            if zone_low <= close[i] <= zone_high:
                touches += 1

        if touches >= self.min_touches:
            confidence = min(touches / 5.0, 1.0)

            return SMCPattern(
                pattern_type=SMCType.LIQUIDITY_ZONE,
                start_index=0,
                end_index=len(close) - 1,
                high=zone_high,
                low=zone_low,
                confidence=confidence,
                metadata={
                    "zone_type": zone_type,
                    "level": level,
                    "touches": touches,
                    "zone_size": zone_size,
                },
            )

        return None


class SMCAnalyzer:
    """
    Comprehensive Smart Money Concepts analyzer.

    Combines all SMC detectors to provide complete analysis.
    """

    def __init__(self):
        """Initialize SMC analyzer."""
        self.order_block_detector = OrderBlockDetector()
        self.fvg_detector = FairValueGapDetector()
        self.bos_detector = BreakOfStructureDetector()
        self.liquidity_detector = LiquidityZoneDetector()

        logger.info("SMCAnalyzer initialized with all detectors")

    def analyze(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray
    ) -> Dict[str, List[SMCPattern]]:
        """
        Perform comprehensive SMC analysis.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            volume: Volume data

        Returns:
            Dictionary of detected patterns by type
        """
        results = {}

        # Detect order blocks
        bullish_ob = self.order_block_detector.detect_bullish_order_blocks(
            high, low, close, volume
        )
        bearish_ob = self.order_block_detector.detect_bearish_order_blocks(
            high, low, close, volume
        )
        results["order_blocks"] = bullish_ob + bearish_ob

        # Detect fair value gaps
        results["fair_value_gaps"] = self.fvg_detector.detect_fair_value_gaps(
            high, low, close
        )

        # Detect break of structure
        results["break_of_structure"] = self.bos_detector.detect_break_of_structure(
            high, low, close
        )

        # Detect liquidity zones
        results["liquidity_zones"] = self.liquidity_detector.detect_liquidity_zones(
            high, low, close
        )

        return results

    def get_smc_features(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray
    ) -> np.ndarray:
        """
        Extract SMC features for machine learning.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            volume: Volume data

        Returns:
            Feature array
        """
        features = []

        # Analyze SMC patterns
        smc_results = self.analyze(high, low, close, volume)

        # Extract features
        for i in range(len(close)):
            feature_vector = []

            # Order block features
            ob_count = sum(
                1
                for ob in smc_results["order_blocks"]
                if ob.start_index <= i <= ob.end_index
            )
            feature_vector.append(ob_count)

            # FVG features
            fvg_count = sum(
                1
                for fvg in smc_results["fair_value_gaps"]
                if fvg.start_index <= i <= fvg.end_index
            )
            feature_vector.append(fvg_count)

            # BOS features
            bos_count = sum(
                1
                for bos in smc_results["break_of_structure"]
                if bos.start_index <= i <= bos.end_index
            )
            feature_vector.append(bos_count)

            # Liquidity zone features
            lz_count = sum(
                1
                for lz in smc_results["liquidity_zones"]
                if lz.low <= close[i] <= lz.high
            )
            feature_vector.append(lz_count)

            features.append(feature_vector)

        return np.array(features)
