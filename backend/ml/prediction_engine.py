"""
Bull/Bear Prediction Engine with Uncertainty Quantification
Implements Monte Carlo Dropout and temperature scaling for calibrated predictions
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import tensorflow as tf
from tensorflow import keras

logger = logging.getLogger(__name__)


class PredictionType(Enum):
    """Types of predictions."""

    BULL = "bull"
    BEAR = "bear"
    NEUTRAL = "neutral"


@dataclass
class PredictionResult:
    """Prediction result with uncertainty quantification."""

    bullish_probability: float
    bearish_probability: float
    neutral_probability: float
    confidence: float
    uncertainty: float
    prediction: PredictionType
    raw_logits: np.ndarray
    calibrated_logits: np.ndarray
    metadata: Dict[str, Any]
    timestamp: datetime


class UncertaintyQuantifier:
    """
    Uncertainty quantification using Monte Carlo Dropout.

    Features:
    - Monte Carlo Dropout for epistemic uncertainty
    - Temperature scaling for calibration
    - Brier score and ECE calculation
    - Confidence interval estimation
    """

    def __init__(
        self,
        forward_passes: int = 20,
        dropout_rate: float = 0.2,
        temperature: float = 1.0,
        calibration_enabled: bool = True,
    ):
        """
        Initialize uncertainty quantifier.

        Args:
            forward_passes: Number of forward passes for MC Dropout
            dropout_rate: Dropout rate for uncertainty estimation
            temperature: Temperature for calibration
            calibration_enabled: Whether to enable temperature scaling
        """
        self.forward_passes = forward_passes
        self.dropout_rate = dropout_rate
        self.temperature = temperature
        self.calibration_enabled = calibration_enabled

        # Calibration data
        self.calibration_logits = []
        self.calibration_labels = []
        self.temperature_optimized = False

        logger.info(
            f"UncertaintyQuantifier initialized: forward_passes={forward_passes}, "
            f"dropout_rate={dropout_rate}, temperature={temperature}"
        )

    def predict_with_uncertainty(
        self, model: keras.Model, inputs: np.ndarray, training: bool = True
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict with uncertainty quantification using MC Dropout.

        Args:
            model: Keras model
            inputs: Input data
            training: Whether to use dropout (True for uncertainty)

        Returns:
            Tuple of (mean_predictions, uncertainty_estimates)
        """
        predictions = []

        for _ in range(self.forward_passes):
            # Forward pass with dropout
            pred = model(inputs, training=training)
            predictions.append(pred.numpy())

        predictions = np.array(predictions)

        # Calculate mean and uncertainty
        mean_predictions = np.mean(predictions, axis=0)
        uncertainty = np.std(predictions, axis=0)

        return mean_predictions, uncertainty

    def calibrate_temperature(
        self, logits: np.ndarray, labels: np.ndarray, method: str = "scipy"
    ) -> float:
        """
        Calibrate temperature scaling parameter.

        Args:
            logits: Model logits
            labels: True labels
            method: Optimization method ("scipy" or "grid")

        Returns:
            Optimized temperature
        """
        if method == "scipy":
            return self._calibrate_temperature_scipy(logits, labels)
        elif method == "grid":
            return self._calibrate_temperature_grid(logits, labels)
        else:
            raise ValueError(f"Unknown calibration method: {method}")

    def _calibrate_temperature_scipy(
        self, logits: np.ndarray, labels: np.ndarray
    ) -> float:
        """Calibrate temperature using scipy optimization."""
        try:
            from scipy.optimize import minimize_scalar

            def temperature_loss(temp):
                calibrated_logits = logits / temp
                calibrated_probs = tf.nn.softmax(calibrated_logits).numpy()

                # Cross-entropy loss
                loss = -np.mean(
                    np.log(calibrated_probs[np.arange(len(labels)), labels] + 1e-8)
                )
                return loss

            result = minimize_scalar(
                temperature_loss, bounds=(0.1, 10.0), method="bounded"
            )
            optimal_temp = result.x

            self.temperature = optimal_temp
            self.temperature_optimized = True

            logger.info(f"Temperature calibrated to {optimal_temp:.4f}")
            return optimal_temp

        except ImportError:
            logger.warning("Scipy not available, using grid search")
            return self._calibrate_temperature_grid(logits, labels)

    def _calibrate_temperature_grid(
        self, logits: np.ndarray, labels: np.ndarray
    ) -> float:
        """Calibrate temperature using grid search."""
        temperatures = np.logspace(-1, 1, 100)  # 0.1 to 10.0
        best_temp = 1.0
        best_loss = float("inf")

        for temp in temperatures:
            calibrated_logits = logits / temp
            calibrated_probs = tf.nn.softmax(calibrated_logits).numpy()

            # Cross-entropy loss
            loss = -np.mean(
                np.log(calibrated_probs[np.arange(len(labels)), labels] + 1e-8)
            )

            if loss < best_loss:
                best_loss = loss
                best_temp = temp

        self.temperature = best_temp
        self.temperature_optimized = True

        logger.info(f"Temperature calibrated to {best_temp:.4f}")
        return best_temp

    def calculate_brier_score(
        self, predictions: np.ndarray, labels: np.ndarray
    ) -> float:
        """
        Calculate Brier score for calibration assessment.

        Args:
            predictions: Predicted probabilities
            labels: True labels

        Returns:
            Brier score
        """
        # Convert labels to one-hot encoding
        if labels.ndim == 1:
            labels_one_hot = tf.keras.utils.to_categorical(
                labels, num_classes=predictions.shape[1]
            )
        else:
            labels_one_hot = labels

        # Brier score = mean((predicted - actual)^2)
        brier_score = np.mean((predictions - labels_one_hot) ** 2)
        return float(brier_score)

    def calculate_ece(
        self, predictions: np.ndarray, labels: np.ndarray, n_bins: int = 10
    ) -> float:
        """
        Calculate Expected Calibration Error (ECE).

        Args:
            predictions: Predicted probabilities
            labels: True labels
            n_bins: Number of bins for calibration

        Returns:
            ECE score
        """
        if labels.ndim == 1:
            labels_one_hot = tf.keras.utils.to_categorical(
                labels, num_classes=predictions.shape[1]
            )
        else:
            labels_one_hot = labels

        # Get maximum predicted probability and corresponding true label
        max_probs = np.max(predictions, axis=1)
        predicted_labels = np.argmax(predictions, axis=1)
        true_labels = np.argmax(labels_one_hot, axis=1)

        # Calculate ECE
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]

        ece = 0
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            # Find samples in this bin
            in_bin = (max_probs > bin_lower) & (max_probs <= bin_upper)
            prop_in_bin = in_bin.mean()

            if prop_in_bin > 0:
                # Calculate accuracy and confidence in this bin
                accuracy_in_bin = (
                    predicted_labels[in_bin] == true_labels[in_bin]
                ).mean()
                avg_confidence_in_bin = max_probs[in_bin].mean()

                # Add to ECE
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

        return float(ece)


class BullBearPredictionEngine:
    """
    Bull/Bear prediction engine with uncertainty quantification.

    Features:
    - Bull/Bear/Neutral probability distributions
    - Confidence scoring and uncertainty quantification
    - Monte Carlo Dropout for epistemic uncertainty
    - Temperature scaling for calibration
    - Risk-adjusted predictions
    """

    def __init__(
        self,
        model: keras.Model,
        uncertainty_quantifier: Optional[UncertaintyQuantifier] = None,
        confidence_threshold: float = 0.6,
        neutral_threshold: float = 0.1,
    ):
        """
        Initialize prediction engine.

        Args:
            model: Trained Keras model
            uncertainty_quantifier: Uncertainty quantifier instance
            confidence_threshold: Minimum confidence for predictions
            neutral_threshold: Threshold for neutral predictions
        """
        self.model = model
        self.uncertainty_quantifier = uncertainty_quantifier or UncertaintyQuantifier()
        self.confidence_threshold = confidence_threshold
        self.neutral_threshold = neutral_threshold

        # State tracking
        self.prediction_count = 0
        self.calibration_data = []

        logger.info(
            f"BullBearPredictionEngine initialized: confidence_threshold={confidence_threshold}, "
            f"neutral_threshold={neutral_threshold}"
        )

    def predict(
        self,
        inputs: np.ndarray,
        include_uncertainty: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PredictionResult:
        """
        Make bull/bear prediction with uncertainty quantification.

        Args:
            inputs: Input features
            include_uncertainty: Whether to include uncertainty estimation
            metadata: Additional metadata

        Returns:
            Prediction result with uncertainty
        """
        # Ensure inputs have batch dimension
        if inputs.ndim == 1:
            inputs = np.expand_dims(inputs, axis=0)

        # Get predictions with uncertainty
        if include_uncertainty:
            mean_predictions, uncertainty = (
                self.uncertainty_quantifier.predict_with_uncertainty(
                    self.model, inputs, training=True
                )
            )
        else:
            mean_predictions = self.model(inputs, training=False).numpy()
            uncertainty = np.zeros_like(mean_predictions)

        # Apply temperature scaling if calibrated
        if self.uncertainty_quantifier.calibration_enabled:
            calibrated_predictions = (
                mean_predictions / self.uncertainty_quantifier.temperature
            )
        else:
            calibrated_predictions = mean_predictions

        # Convert to probabilities
        raw_probs = tf.nn.softmax(mean_predictions).numpy()
        calibrated_probs = tf.nn.softmax(calibrated_predictions).numpy()

        # Extract probabilities
        bullish_prob = float(calibrated_probs[0, 0])
        bearish_prob = float(calibrated_probs[0, 1])
        neutral_prob = float(calibrated_probs[0, 2])

        # Calculate confidence and uncertainty
        max_prob = max(bullish_prob, bearish_prob, neutral_prob)
        confidence = float(max_prob)
        uncertainty_score = float(np.mean(uncertainty))

        # Determine prediction type
        if neutral_prob > self.neutral_threshold:
            prediction = PredictionType.NEUTRAL
        elif bullish_prob > bearish_prob:
            prediction = PredictionType.BULL
        else:
            prediction = PredictionType.BEAR

        # Create result
        result = PredictionResult(
            bullish_probability=bullish_prob,
            bearish_probability=bearish_prob,
            neutral_probability=neutral_prob,
            confidence=confidence,
            uncertainty=uncertainty_score,
            prediction=prediction,
            raw_logits=mean_predictions[0],
            calibrated_logits=calibrated_predictions[0],
            metadata=metadata or {},
            timestamp=datetime.now(),
        )

        self.prediction_count += 1

        return result

    def predict_batch(
        self,
        inputs: np.ndarray,
        include_uncertainty: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[PredictionResult]:
        """
        Make predictions for a batch of inputs.

        Args:
            inputs: Batch of input features
            include_uncertainty: Whether to include uncertainty estimation
            metadata: Additional metadata

        Returns:
            List of prediction results
        """
        results = []

        for i in range(inputs.shape[0]):
            single_input = inputs[i : i + 1]
            result = self.predict(single_input, include_uncertainty, metadata)
            results.append(result)

        return results

    def calibrate_model(
        self,
        calibration_inputs: np.ndarray,
        calibration_labels: np.ndarray,
        method: str = "scipy",
    ) -> Dict[str, float]:
        """
        Calibrate model using temperature scaling.

        Args:
            calibration_inputs: Calibration inputs
            calibration_labels: Calibration labels
            method: Calibration method

        Returns:
            Calibration metrics
        """
        # Get model predictions
        predictions = self.model(calibration_inputs, training=False).numpy()

        # Calibrate temperature
        optimal_temp = self.uncertainty_quantifier.calibrate_temperature(
            predictions, calibration_labels, method
        )

        # Calculate calibration metrics
        calibrated_predictions = tf.nn.softmax(predictions / optimal_temp).numpy()

        brier_score = self.uncertainty_quantifier.calculate_brier_score(
            calibrated_predictions, calibration_labels
        )

        ece = self.uncertainty_quantifier.calculate_ece(
            calibrated_predictions, calibration_labels
        )

        metrics = {
            "temperature": optimal_temp,
            "brier_score": brier_score,
            "ece": ece,
            "calibration_samples": len(calibration_inputs),
        }

        logger.info(
            f"Model calibrated: temp={optimal_temp:.4f}, brier={brier_score:.4f}, ece={ece:.4f}"
        )

        return metrics

    def get_prediction_stats(self) -> Dict[str, Any]:
        """Get prediction engine statistics."""
        return {
            "prediction_count": self.prediction_count,
            "confidence_threshold": self.confidence_threshold,
            "neutral_threshold": self.neutral_threshold,
            "uncertainty_quantifier": {
                "forward_passes": self.uncertainty_quantifier.forward_passes,
                "dropout_rate": self.uncertainty_quantifier.dropout_rate,
                "temperature": self.uncertainty_quantifier.temperature,
                "calibration_enabled": self.uncertainty_quantifier.calibration_enabled,
                "temperature_optimized": self.uncertainty_quantifier.temperature_optimized,
            },
        }

    def update_confidence_threshold(self, new_threshold: float) -> None:
        """Update confidence threshold."""
        self.confidence_threshold = new_threshold
        logger.info(f"Confidence threshold updated to {new_threshold}")

    def update_neutral_threshold(self, new_threshold: float) -> None:
        """Update neutral threshold."""
        self.neutral_threshold = new_threshold
        logger.info(f"Neutral threshold updated to {new_threshold}")


def create_prediction_engine(
    model: keras.Model,
    forward_passes: int = 20,
    dropout_rate: float = 0.2,
    confidence_threshold: float = 0.6,
    neutral_threshold: float = 0.1,
    calibration_enabled: bool = True,
) -> BullBearPredictionEngine:
    """
    Factory function to create prediction engine.

    Args:
        model: Trained Keras model
        forward_passes: Number of forward passes for MC Dropout
        dropout_rate: Dropout rate for uncertainty estimation
        confidence_threshold: Minimum confidence for predictions
        neutral_threshold: Threshold for neutral predictions
        calibration_enabled: Whether to enable calibration

    Returns:
        Configured prediction engine
    """
    uncertainty_quantifier = UncertaintyQuantifier(
        forward_passes=forward_passes,
        dropout_rate=dropout_rate,
        calibration_enabled=calibration_enabled,
    )

    return BullBearPredictionEngine(
        model=model,
        uncertainty_quantifier=uncertainty_quantifier,
        confidence_threshold=confidence_threshold,
        neutral_threshold=neutral_threshold,
    )
