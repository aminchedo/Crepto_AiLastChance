"""
Curriculum Learning & Market Regime Awareness
Progressive training with timeframe curriculum and regime detection
"""

import logging
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class Timeframe(Enum):
    """Trading timeframes."""

    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    DAY_1 = "1d"
    WEEK_1 = "1w"


class MarketRegime(Enum):
    """Market regime types."""

    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    TRENDING = "trending"
    MEAN_REVERTING = "mean_reverting"


@dataclass
class CurriculumStage:
    """Curriculum learning stage."""

    stage_id: int
    name: str
    timeframe: Timeframe
    min_accuracy: float
    min_r2: float
    min_samples: int
    max_samples: int
    difficulty_weight: float
    description: str


@dataclass
class RegimeFeatures:
    """Market regime features."""

    regime: MarketRegime
    confidence: float
    volatility_regime: str
    trend_strength: float
    mean_reversion_strength: float
    volume_profile: str
    features: Dict[str, float]


class TimeframeCurriculum:
    """
    Timeframe-based curriculum learning.

    Progressively trains the model on longer timeframes first,
    then moves to shorter timeframes as performance improves.
    """

    def __init__(
        self,
        start_timeframe: Timeframe = Timeframe.HOUR_4,
        end_timeframe: Timeframe = Timeframe.MINUTE_1,
        progression_threshold: float = 0.7,
    ):
        """
        Initialize timeframe curriculum.

        Args:
            start_timeframe: Starting timeframe
            end_timeframe: Target timeframe
            progression_threshold: Accuracy threshold for progression
        """
        self.start_timeframe = start_timeframe
        self.end_timeframe = end_timeframe
        self.progression_threshold = progression_threshold

        # Define curriculum stages
        self.stages = self._create_curriculum_stages()
        self.current_stage = 0

        logger.info(
            f"TimeframeCurriculum initialized: {start_timeframe.value} → {end_timeframe.value}"
        )

    def _create_curriculum_stages(self) -> List[CurriculumStage]:
        """Create curriculum stages."""
        timeframes = [
            Timeframe.WEEK_1,
            Timeframe.DAY_1,
            Timeframe.HOUR_4,
            Timeframe.HOUR_1,
            Timeframe.MINUTE_30,
            Timeframe.MINUTE_15,
            Timeframe.MINUTE_5,
            Timeframe.MINUTE_1,
        ]

        # Find start and end indices
        start_idx = timeframes.index(self.start_timeframe)
        end_idx = timeframes.index(self.end_timeframe)

        stages = []
        for i, tf in enumerate(timeframes[start_idx : end_idx + 1]):
            stage_id = i
            difficulty_weight = 1.0 - (i * 0.1)  # Decreasing difficulty

            stages.append(
                CurriculumStage(
                    stage_id=stage_id,
                    name=f"Stage {stage_id + 1}: {tf.value}",
                    timeframe=tf,
                    min_accuracy=0.6 + (i * 0.05),  # Increasing accuracy requirement
                    min_r2=0.3 + (i * 0.1),  # Increasing R² requirement
                    min_samples=1000 + (i * 500),  # Increasing sample requirement
                    max_samples=5000 + (i * 2000),  # Increasing max samples
                    difficulty_weight=difficulty_weight,
                    description=f"Training on {tf.value} timeframe",
                )
            )

        return stages

    def get_current_stage(self) -> CurriculumStage:
        """Get current curriculum stage."""
        if self.current_stage < len(self.stages):
            return self.stages[self.current_stage]
        return self.stages[-1]  # Return last stage if completed

    def evaluate_progression(
        self, accuracy: float, r2_score: float, sample_count: int
    ) -> bool:
        """
        Evaluate if model is ready to progress to next stage.

        Args:
            accuracy: Current accuracy
            r2_score: Current R² score
            sample_count: Number of training samples

        Returns:
            True if ready to progress, False otherwise
        """
        current_stage = self.get_current_stage()

        # Check progression criteria
        accuracy_ok = accuracy >= current_stage.min_accuracy
        r2_ok = r2_score >= current_stage.min_r2
        samples_ok = sample_count >= current_stage.min_samples

        return accuracy_ok and r2_ok and samples_ok

    def progress_to_next_stage(self) -> bool:
        """
        Progress to next curriculum stage.

        Returns:
            True if progressed, False if already at final stage
        """
        if self.current_stage < len(self.stages) - 1:
            self.current_stage += 1
            logger.info(
                f"Progressed to stage {self.current_stage}: {self.get_current_stage().name}"
            )
            return True
        return False

    def get_training_config(self) -> Dict[str, Any]:
        """Get training configuration for current stage."""
        current_stage = self.get_current_stage()

        return {
            "timeframe": current_stage.timeframe.value,
            "min_samples": current_stage.min_samples,
            "max_samples": current_stage.max_samples,
            "difficulty_weight": current_stage.difficulty_weight,
            "stage_name": current_stage.name,
            "description": current_stage.description,
        }

    def reset_curriculum(self):
        """Reset curriculum to first stage."""
        self.current_stage = 0
        logger.info("Curriculum reset to first stage")


class MarketRegimeDetector:
    """
    Market regime detection and classification.

    Identifies different market regimes based on price action,
    volatility, and volume patterns.
    """

    def __init__(
        self,
        lookback_period: int = 50,
        volatility_threshold: float = 0.02,
        trend_threshold: float = 0.1,
    ):
        """
        Initialize market regime detector.

        Args:
            lookback_period: Period for regime analysis
            volatility_threshold: Volatility threshold for regime classification
            trend_threshold: Trend strength threshold
        """
        self.lookback_period = lookback_period
        self.volatility_threshold = volatility_threshold
        self.trend_threshold = trend_threshold

        logger.info(f"MarketRegimeDetector initialized: lookback={lookback_period}")

    def detect_regime(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray
    ) -> RegimeFeatures:
        """
        Detect current market regime.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            volume: Volume data

        Returns:
            Regime features
        """
        if len(close) < self.lookback_period:
            return self._get_default_regime()

        # Calculate regime features
        volatility = self._calculate_volatility(close)
        trend_strength = self._calculate_trend_strength(close)
        mean_reversion_strength = self._calculate_mean_reversion_strength(close)
        volume_profile = self._analyze_volume_profile(volume)

        # Classify regime
        regime = self._classify_regime(
            volatility, trend_strength, mean_reversion_strength, volume_profile
        )

        # Calculate confidence
        confidence = self._calculate_regime_confidence(
            volatility, trend_strength, mean_reversion_strength
        )

        # Determine volatility regime
        volatility_regime = self._classify_volatility_regime(volatility)

        return RegimeFeatures(
            regime=regime,
            confidence=confidence,
            volatility_regime=volatility_regime,
            trend_strength=trend_strength,
            mean_reversion_strength=mean_reversion_strength,
            volume_profile=volume_profile,
            features={
                "volatility": volatility,
                "trend_strength": trend_strength,
                "mean_reversion_strength": mean_reversion_strength,
                "volume_ratio": (
                    np.mean(volume[-10:]) / np.mean(volume[-50:-10])
                    if len(volume) >= 50
                    else 1.0
                ),
            },
        )

    def _calculate_volatility(self, close: np.ndarray) -> float:
        """Calculate price volatility."""
        if len(close) < 2:
            return 0.0

        returns = np.diff(close) / close[:-1]
        return np.std(returns)

    def _calculate_trend_strength(self, close: np.ndarray) -> float:
        """Calculate trend strength using linear regression."""
        if len(close) < self.lookback_period:
            return 0.0

        recent_close = close[-self.lookback_period :]
        x = np.arange(len(recent_close))

        # Linear regression
        slope, intercept = np.polyfit(x, recent_close, 1)

        # Normalize slope by price level
        trend_strength = abs(slope) / np.mean(recent_close)

        return trend_strength

    def _calculate_mean_reversion_strength(self, close: np.ndarray) -> float:
        """Calculate mean reversion strength."""
        if len(close) < self.lookback_period:
            return 0.0

        recent_close = close[-self.lookback_period :]

        # Calculate mean reversion using autocorrelation
        returns = np.diff(recent_close) / recent_close[:-1]

        if len(returns) < 2:
            return 0.0

        # First-order autocorrelation
        autocorr = np.corrcoef(returns[:-1], returns[1:])[0, 1]

        # Mean reversion strength (negative autocorrelation)
        mean_reversion_strength = max(0, -autocorr)

        return mean_reversion_strength

    def _analyze_volume_profile(self, volume: np.ndarray) -> str:
        """Analyze volume profile."""
        if len(volume) < self.lookback_period:
            return "normal"

        recent_volume = volume[-self.lookback_period :]
        avg_volume = (
            np.mean(volume[: -self.lookback_period])
            if len(volume) > self.lookback_period
            else np.mean(recent_volume)
        )

        volume_ratio = np.mean(recent_volume) / avg_volume

        if volume_ratio > 1.5:
            return "high"
        elif volume_ratio < 0.7:
            return "low"
        else:
            return "normal"

    def _classify_regime(
        self,
        volatility: float,
        trend_strength: float,
        mean_reversion_strength: float,
        volume_profile: str,
    ) -> MarketRegime:
        """Classify market regime based on features."""

        # High volatility regime
        if volatility > self.volatility_threshold * 2:
            return MarketRegime.HIGH_VOLATILITY

        # Low volatility regime
        if volatility < self.volatility_threshold * 0.5:
            return MarketRegime.LOW_VOLATILITY

        # Trending regime
        if trend_strength > self.trend_threshold:
            return MarketRegime.TRENDING

        # Mean reverting regime
        if mean_reversion_strength > 0.3:
            return MarketRegime.MEAN_REVERTING

        # Bull/Bear/Sideways based on trend direction
        if len(close) >= self.lookback_period:
            recent_close = close[-self.lookback_period :]
            price_change = (recent_close[-1] - recent_close[0]) / recent_close[0]

            if price_change > 0.05:  # 5% increase
                return MarketRegime.BULL
            elif price_change < -0.05:  # 5% decrease
                return MarketRegime.BEAR
            else:
                return MarketRegime.SIDEWAYS

        return MarketRegime.SIDEWAYS

    def _classify_volatility_regime(self, volatility: float) -> str:
        """Classify volatility regime."""
        if volatility > self.volatility_threshold * 2:
            return "very_high"
        elif volatility > self.volatility_threshold * 1.5:
            return "high"
        elif volatility > self.volatility_threshold:
            return "normal"
        elif volatility > self.volatility_threshold * 0.5:
            return "low"
        else:
            return "very_low"

    def _calculate_regime_confidence(
        self, volatility: float, trend_strength: float, mean_reversion_strength: float
    ) -> float:
        """Calculate regime classification confidence."""
        confidence = 0.0

        # Volatility confidence
        if (
            volatility > self.volatility_threshold * 2
            or volatility < self.volatility_threshold * 0.5
        ):
            confidence += 0.3

        # Trend confidence
        if trend_strength > self.trend_threshold:
            confidence += 0.3

        # Mean reversion confidence
        if mean_reversion_strength > 0.3:
            confidence += 0.2

        # Base confidence
        confidence += 0.2

        return min(confidence, 1.0)

    def _get_default_regime(self) -> RegimeFeatures:
        """Get default regime when insufficient data."""
        return RegimeFeatures(
            regime=MarketRegime.SIDEWAYS,
            confidence=0.0,
            volatility_regime="normal",
            trend_strength=0.0,
            mean_reversion_strength=0.0,
            volume_profile="normal",
            features={},
        )


class RegimeAwareTraining:
    """
    Regime-aware training that adapts to different market conditions.
    """

    def __init__(
        self, curriculum: TimeframeCurriculum, regime_detector: MarketRegimeDetector
    ):
        """
        Initialize regime-aware training.

        Args:
            curriculum: Timeframe curriculum
            regime_detector: Market regime detector
        """
        self.curriculum = curriculum
        self.regime_detector = regime_detector

        # Regime-specific training parameters
        self.regime_configs = {
            MarketRegime.BULL: {
                "learning_rate_multiplier": 1.2,
                "batch_size_multiplier": 1.0,
                "regularization_multiplier": 0.8,
            },
            MarketRegime.BEAR: {
                "learning_rate_multiplier": 0.8,
                "batch_size_multiplier": 1.2,
                "regularization_multiplier": 1.2,
            },
            MarketRegime.SIDEWAYS: {
                "learning_rate_multiplier": 1.0,
                "batch_size_multiplier": 1.0,
                "regularization_multiplier": 1.0,
            },
            MarketRegime.HIGH_VOLATILITY: {
                "learning_rate_multiplier": 0.7,
                "batch_size_multiplier": 1.5,
                "regularization_multiplier": 1.5,
            },
            MarketRegime.LOW_VOLATILITY: {
                "learning_rate_multiplier": 1.3,
                "batch_size_multiplier": 0.8,
                "regularization_multiplier": 0.7,
            },
            MarketRegime.TRENDING: {
                "learning_rate_multiplier": 1.1,
                "batch_size_multiplier": 1.0,
                "regularization_multiplier": 0.9,
            },
            MarketRegime.MEAN_REVERTING: {
                "learning_rate_multiplier": 0.9,
                "batch_size_multiplier": 1.1,
                "regularization_multiplier": 1.1,
            },
        }

        logger.info("RegimeAwareTraining initialized")

    def get_training_config(
        self, base_config: Dict[str, Any], market_data: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Get regime-aware training configuration.

        Args:
            base_config: Base training configuration
            market_data: Market data for regime detection

        Returns:
            Adapted training configuration
        """
        # Detect current regime
        regime_features = self.regime_detector.detect_regime(
            market_data["high"],
            market_data["low"],
            market_data["close"],
            market_data["volume"],
        )

        # Get curriculum stage
        curriculum_config = self.curriculum.get_training_config()

        # Get regime-specific multipliers
        regime_config = self.regime_configs[regime_features.regime]

        # Adapt configuration
        adapted_config = base_config.copy()
        adapted_config.update(curriculum_config)

        # Apply regime-specific adjustments
        adapted_config["learning_rate"] *= regime_config["learning_rate_multiplier"]
        adapted_config["batch_size"] = int(
            adapted_config["batch_size"] * regime_config["batch_size_multiplier"]
        )
        adapted_config["regularization"] *= regime_config["regularization_multiplier"]

        # Add regime information
        adapted_config["regime"] = regime_features.regime.value
        adapted_config["regime_confidence"] = regime_features.confidence
        adapted_config["volatility_regime"] = regime_features.volatility_regime
        adapted_config["trend_strength"] = regime_features.trend_strength
        adapted_config["mean_reversion_strength"] = (
            regime_features.mean_reversion_strength
        )

        return adapted_config

    def should_adapt_training(
        self,
        current_regime: MarketRegime,
        previous_regime: MarketRegime,
        regime_confidence: float,
    ) -> bool:
        """
        Determine if training should be adapted based on regime change.

        Args:
            current_regime: Current market regime
            previous_regime: Previous market regime
            regime_confidence: Confidence in regime classification

        Returns:
            True if training should be adapted
        """
        # Adapt if regime changed and confidence is high
        if current_regime != previous_regime and regime_confidence > 0.7:
            return True

        # Adapt if confidence increased significantly
        if regime_confidence > 0.8:
            return True

        return False

    def get_regime_features(self, market_data: Dict[str, np.ndarray]) -> RegimeFeatures:
        """Get current regime features."""
        return self.regime_detector.detect_regime(
            market_data["high"],
            market_data["low"],
            market_data["close"],
            market_data["volume"],
        )


class CurriculumManager:
    """
    Comprehensive curriculum learning manager.
    """

    def __init__(
        self,
        start_timeframe: Timeframe = Timeframe.HOUR_4,
        end_timeframe: Timeframe = Timeframe.MINUTE_1,
        lookback_period: int = 50,
    ):
        """
        Initialize curriculum manager.

        Args:
            start_timeframe: Starting timeframe
            end_timeframe: Target timeframe
            lookback_period: Regime detection lookback period
        """
        self.curriculum = TimeframeCurriculum(start_timeframe, end_timeframe)
        self.regime_detector = MarketRegimeDetector(lookback_period)
        self.regime_aware_training = RegimeAwareTraining(
            self.curriculum, self.regime_detector
        )

        self.training_history = []
        self.regime_history = []

        logger.info("CurriculumManager initialized")

    def update_training_progress(
        self, accuracy: float, r2_score: float, sample_count: int, epoch: int
    ) -> bool:
        """
        Update training progress and check for curriculum progression.

        Args:
            accuracy: Current accuracy
            r2_score: Current R² score
            sample_count: Number of training samples
            epoch: Current epoch

        Returns:
            True if progressed to next stage
        """
        # Record training progress
        self.training_history.append(
            {
                "epoch": epoch,
                "accuracy": accuracy,
                "r2_score": r2_score,
                "sample_count": sample_count,
                "stage": self.curriculum.current_stage,
                "timestamp": datetime.now(),
            }
        )

        # Check for progression
        if self.curriculum.evaluate_progression(accuracy, r2_score, sample_count):
            return self.curriculum.progress_to_next_stage()

        return False

    def get_adaptive_training_config(
        self, base_config: Dict[str, Any], market_data: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """Get adaptive training configuration."""
        return self.regime_aware_training.get_training_config(base_config, market_data)

    def get_current_regime(self, market_data: Dict[str, np.ndarray]) -> RegimeFeatures:
        """Get current market regime."""
        regime_features = self.regime_aware_training.get_regime_features(market_data)

        # Record regime history
        self.regime_history.append(
            {
                "regime": regime_features.regime.value,
                "confidence": regime_features.confidence,
                "timestamp": datetime.now(),
            }
        )

        return regime_features

    def get_curriculum_status(self) -> Dict[str, Any]:
        """Get current curriculum status."""
        current_stage = self.curriculum.get_current_stage()

        return {
            "current_stage": current_stage.stage_id,
            "stage_name": current_stage.name,
            "timeframe": current_stage.timeframe.value,
            "min_accuracy": current_stage.min_accuracy,
            "min_r2": current_stage.min_r2,
            "min_samples": current_stage.min_samples,
            "difficulty_weight": current_stage.difficulty_weight,
            "total_stages": len(self.curriculum.stages),
            "is_complete": self.curriculum.current_stage
            >= len(self.curriculum.stages) - 1,
        }

    def get_training_summary(self) -> Dict[str, Any]:
        """Get training summary."""
        if not self.training_history:
            return {}

        latest = self.training_history[-1]

        return {
            "total_epochs": latest["epoch"],
            "current_accuracy": latest["accuracy"],
            "current_r2": latest["r2_score"],
            "current_stage": latest["stage"],
            "total_samples": latest["sample_count"],
            "training_duration": (
                latest["timestamp"] - self.training_history[0]["timestamp"]
            ).total_seconds()
            / 3600,  # hours
        }

    def reset_curriculum(self):
        """Reset curriculum to beginning."""
        self.curriculum.reset_curriculum()
        self.training_history.clear()
        self.regime_history.clear()
        logger.info("Curriculum reset")
