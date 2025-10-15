"""
Instability Detection & Recovery System
Monitors training for numerical instability and triggers automatic recovery
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import tensorflow as tf

logger = logging.getLogger(__name__)


class InstabilityType(Enum):
    """Types of instability that can be detected."""

    NAN_INF = "nan_inf"
    GRADIENT_SPIKE = "gradient_spike"
    LOSS_SPIKE = "loss_spike"
    VALIDATION_COLLAPSE = "validation_collapse"
    LEARNING_RATE_TOO_HIGH = "learning_rate_too_high"
    WEIGHT_EXPLOSION = "weight_explosion"


@dataclass
class InstabilityEvent:
    """Record of an instability event."""

    timestamp: datetime
    event_type: InstabilityType
    epoch: int
    batch: int
    value: float
    threshold: float
    context: Dict[str, Any]
    severity: str  # 'low', 'medium', 'high', 'critical'


class InstabilityMonitor:
    """
    Monitors neural network training for signs of instability.

    Detects:
    - NaN/Inf values in gradients, weights, or activations
    - Gradient norm spikes
    - Loss spikes (sudden increases)
    - Validation performance collapse
    - Learning rate too high
    - Weight explosion
    """

    def __init__(
        self,
        spike_factor: float = 3.0,
        gradient_spike_factor: float = 2.5,
        ema_smoothing: float = 0.1,
        min_samples: int = 10,
        validation_patience: int = 5,
        max_gradient_norm: float = 10.0,
        max_weight_norm: float = 100.0,
        max_learning_rate: float = 0.1,
    ):
        """
        Initialize instability monitor.

        Args:
            spike_factor: Factor for detecting loss spikes (multiplier of EMA)
            gradient_spike_factor: Factor for detecting gradient spikes
            ema_smoothing: EMA smoothing factor for loss tracking
            min_samples: Minimum samples before monitoring starts
            validation_patience: Patience for validation collapse detection
            max_gradient_norm: Maximum acceptable gradient norm
            max_weight_norm: Maximum acceptable weight norm
            max_learning_rate: Maximum acceptable learning rate
        """
        self.spike_factor = spike_factor
        self.gradient_spike_factor = gradient_spike_factor
        self.ema_smoothing = ema_smoothing
        self.min_samples = min_samples
        self.validation_patience = validation_patience
        self.max_gradient_norm = max_gradient_norm
        self.max_weight_norm = max_weight_norm
        self.max_learning_rate = max_learning_rate

        # State tracking
        self.loss_ema = None
        self.gradient_norm_ema = None
        self.validation_loss_history = []
        self.instability_events = []
        self.sample_count = 0

        # Statistics
        self.total_resets = 0
        self.last_reset_epoch = -1

        logger.info(
            f"Instability monitor initialized: spike_factor={spike_factor}, "
            f"gradient_spike_factor={gradient_spike_factor}, ema_smoothing={ema_smoothing}"
        )

    def check_nan_inf(
        self, tensor: tf.Tensor, name: str, epoch: int, batch: int
    ) -> Optional[InstabilityEvent]:
        """
        Check for NaN or Inf values in tensor.

        Args:
            tensor: Tensor to check
            name: Name of tensor for logging
            epoch: Current epoch
            batch: Current batch

        Returns:
            InstabilityEvent if NaN/Inf detected, None otherwise
        """
        # Convert to numpy for checking
        if hasattr(tensor, "numpy"):
            values = tensor.numpy()
        else:
            values = tensor

        has_nan = np.any(np.isnan(values))
        has_inf = np.any(np.isinf(values))

        if has_nan or has_inf:
            severity = "critical" if has_nan else "high"

            event = InstabilityEvent(
                timestamp=datetime.now(),
                event_type=InstabilityType.NAN_INF,
                epoch=epoch,
                batch=batch,
                value=float("inf") if has_inf else float("nan"),
                threshold=0.0,
                context={
                    "tensor_name": name,
                    "shape": values.shape,
                    "has_nan": has_nan,
                    "has_inf": has_inf,
                    "nan_count": np.sum(np.isnan(values)) if has_nan else 0,
                    "inf_count": np.sum(np.isinf(values)) if has_inf else 0,
                },
                severity=severity,
            )

            self.instability_events.append(event)

            logger.error(
                f"NaN/Inf detected in {name}: NaN={has_nan}, Inf={has_inf}, "
                f"shape={values.shape}, epoch={epoch}, batch={batch}"
            )

            return event

        return None

    def check_gradient_spike(
        self, gradient_norm: float, epoch: int, batch: int
    ) -> Optional[InstabilityEvent]:
        """
        Check for gradient norm spikes.

        Args:
            gradient_norm: Current gradient norm
            epoch: Current epoch
            batch: Current batch

        Returns:
            InstabilityEvent if spike detected, None otherwise
        """
        # Update EMA
        if self.gradient_norm_ema is None:
            self.gradient_norm_ema = gradient_norm
        else:
            self.gradient_norm_ema = (
                self.ema_smoothing * gradient_norm
                + (1 - self.ema_smoothing) * self.gradient_norm_ema
            )

        # Check for spike
        if self.sample_count >= self.min_samples:
            threshold = self.gradient_norm_ema * self.gradient_spike_factor

            if gradient_norm > threshold:
                severity = (
                    "high" if gradient_norm > self.max_gradient_norm else "medium"
                )

                event = InstabilityEvent(
                    timestamp=datetime.now(),
                    event_type=InstabilityType.GRADIENT_SPIKE,
                    epoch=epoch,
                    batch=batch,
                    value=gradient_norm,
                    threshold=threshold,
                    context={
                        "gradient_norm_ema": self.gradient_norm_ema,
                        "spike_factor": self.gradient_spike_factor,
                        "max_gradient_norm": self.max_gradient_norm,
                    },
                    severity=severity,
                )

                self.instability_events.append(event)

                logger.warning(
                    f"Gradient spike detected: norm={gradient_norm:.4f}, "
                    f"threshold={threshold:.4f}, EMA={self.gradient_norm_ema:.4f}, "
                    f"epoch={epoch}, batch={batch}"
                )

                return event

        return None

    def check_loss_spike(
        self, loss: float, epoch: int, batch: int
    ) -> Optional[InstabilityEvent]:
        """
        Check for loss spikes.

        Args:
            loss: Current loss value
            epoch: Current epoch
            batch: Current batch

        Returns:
            InstabilityEvent if spike detected, None otherwise
        """
        # Update EMA
        if self.loss_ema is None:
            self.loss_ema = loss
        else:
            self.loss_ema = (
                self.ema_smoothing * loss + (1 - self.ema_smoothing) * self.loss_ema
            )

        # Check for spike
        if self.sample_count >= self.min_samples:
            threshold = self.loss_ema * self.spike_factor

            if loss > threshold:
                severity = "high" if loss > threshold * 2 else "medium"

                event = InstabilityEvent(
                    timestamp=datetime.now(),
                    event_type=InstabilityType.LOSS_SPIKE,
                    epoch=epoch,
                    batch=batch,
                    value=loss,
                    threshold=threshold,
                    context={
                        "loss_ema": self.loss_ema,
                        "spike_factor": self.spike_factor,
                    },
                    severity=severity,
                )

                self.instability_events.append(event)

                logger.warning(
                    f"Loss spike detected: loss={loss:.4f}, "
                    f"threshold={threshold:.4f}, EMA={self.loss_ema:.4f}, "
                    f"epoch={epoch}, batch={batch}"
                )

                return event

        return None

    def check_validation_collapse(
        self, validation_loss: float, epoch: int
    ) -> Optional[InstabilityEvent]:
        """
        Check for validation performance collapse.

        Args:
            validation_loss: Current validation loss
            epoch: Current epoch

        Returns:
            InstabilityEvent if collapse detected, None otherwise
        """
        self.validation_loss_history.append(validation_loss)

        # Need enough history to detect collapse
        if len(self.validation_loss_history) < self.validation_patience:
            return None

        # Check if validation loss is consistently increasing
        recent_losses = self.validation_loss_history[-self.validation_patience :]
        is_increasing = all(
            recent_losses[i] <= recent_losses[i + 1]
            for i in range(len(recent_losses) - 1)
        )

        # Check for significant increase
        if len(self.validation_loss_history) >= self.validation_patience * 2:
            old_avg = np.mean(
                self.validation_loss_history[
                    -self.validation_patience * 2 : -self.validation_patience
                ]
            )
            new_avg = np.mean(recent_losses)
            increase_ratio = new_avg / old_avg if old_avg > 0 else 1.0

            if is_increasing and increase_ratio > 1.5:
                event = InstabilityEvent(
                    timestamp=datetime.now(),
                    event_type=InstabilityType.VALIDATION_COLLAPSE,
                    epoch=epoch,
                    batch=0,
                    value=validation_loss,
                    threshold=old_avg * 1.5,
                    context={
                        "validation_loss_history": recent_losses,
                        "increase_ratio": increase_ratio,
                        "patience": self.validation_patience,
                    },
                    severity="medium",
                )

                self.instability_events.append(event)

                logger.warning(
                    f"Validation collapse detected: current={validation_loss:.4f}, "
                    f"old_avg={old_avg:.4f}, increase_ratio={increase_ratio:.2f}, "
                    f"epoch={epoch}"
                )

                return event

        return None

    def check_learning_rate(
        self, learning_rate: float, epoch: int
    ) -> Optional[InstabilityEvent]:
        """
        Check if learning rate is too high.

        Args:
            learning_rate: Current learning rate
            epoch: Current epoch

        Returns:
            InstabilityEvent if LR too high, None otherwise
        """
        if learning_rate > self.max_learning_rate:
            event = InstabilityEvent(
                timestamp=datetime.now(),
                event_type=InstabilityType.LEARNING_RATE_TOO_HIGH,
                epoch=epoch,
                batch=0,
                value=learning_rate,
                threshold=self.max_learning_rate,
                context={
                    "max_learning_rate": self.max_learning_rate,
                },
                severity="medium",
            )

            self.instability_events.append(event)

            logger.warning(
                f"Learning rate too high: {learning_rate:.6f} > {self.max_learning_rate:.6f}, "
                f"epoch={epoch}"
            )

            return event

        return None

    def check_weight_norms(
        self, model: tf.keras.Model, epoch: int
    ) -> Optional[InstabilityEvent]:
        """
        Check for weight explosion.

        Args:
            model: Keras model to check
            epoch: Current epoch

        Returns:
            InstabilityEvent if weights exploded, None otherwise
        """
        max_weight_norm = 0.0
        weight_stats = {}

        for layer in model.layers:
            if hasattr(layer, "weights") and layer.weights:
                for weight in layer.weights:
                    weight_norm = tf.norm(weight).numpy()
                    max_weight_norm = max(max_weight_norm, weight_norm)

                    weight_stats[layer.name] = {
                        "weight_norm": weight_norm,
                        "weight_count": len(layer.weights),
                    }

        if max_weight_norm > self.max_weight_norm:
            event = InstabilityEvent(
                timestamp=datetime.now(),
                event_type=InstabilityType.WEIGHT_EXPLOSION,
                epoch=epoch,
                batch=0,
                value=max_weight_norm,
                threshold=self.max_weight_norm,
                context={
                    "max_weight_norm": self.max_weight_norm,
                    "weight_stats": weight_stats,
                },
                severity="high",
            )

            self.instability_events.append(event)

            logger.error(
                f"Weight explosion detected: max_norm={max_weight_norm:.4f} > "
                f"{self.max_weight_norm:.4f}, epoch={epoch}"
            )

            return event

        return None

    def monitor_batch(
        self,
        loss: float,
        gradient_norm: float,
        epoch: int,
        batch: int,
        model: tf.keras.Model,
        learning_rate: float,
    ) -> List[InstabilityEvent]:
        """
        Monitor a single training batch for instability.

        Args:
            loss: Training loss
            gradient_norm: Gradient norm
            epoch: Current epoch
            batch: Current batch
            model: Keras model
            learning_rate: Current learning rate

        Returns:
            List of detected instability events
        """
        self.sample_count += 1
        events = []

        # Check for NaN/Inf in loss
        if np.isnan(loss) or np.isinf(loss):
            event = self.check_nan_inf(tf.constant(loss), "loss", epoch, batch)
            if event:
                events.append(event)

        # Check gradient spike
        if not np.isnan(gradient_norm) and not np.isinf(gradient_norm):
            event = self.check_gradient_spike(gradient_norm, epoch, batch)
            if event:
                events.append(event)

        # Check loss spike
        if not np.isnan(loss) and not np.isinf(loss):
            event = self.check_loss_spike(loss, epoch, batch)
            if event:
                events.append(event)

        # Check learning rate
        event = self.check_learning_rate(learning_rate, epoch)
        if event:
            events.append(event)

        # Check weight norms (less frequently)
        if batch % 100 == 0:
            event = self.check_weight_norms(model, epoch)
            if event:
                events.append(event)

        return events

    def monitor_epoch(
        self, validation_loss: float, epoch: int
    ) -> List[InstabilityEvent]:
        """
        Monitor epoch-end for instability.

        Args:
            validation_loss: Validation loss
            epoch: Current epoch

        Returns:
            List of detected instability events
        """
        events = []

        # Check validation collapse
        event = self.check_validation_collapse(validation_loss, epoch)
        if event:
            events.append(event)

        return events

    def should_reset(self, events: List[InstabilityEvent]) -> bool:
        """
        Determine if training should be reset based on instability events.

        Args:
            events: List of instability events

        Returns:
            True if reset is recommended
        """
        if not events:
            return False

        # Reset on critical events
        critical_events = [
            e
            for e in events
            if e.severity == "critical" or e.event_type == InstabilityType.NAN_INF
        ]

        if critical_events:
            return True

        # Reset on multiple high-severity events
        high_severity_events = [e for e in events if e.severity == "high"]

        if len(high_severity_events) >= 2:
            return True

        # Reset on weight explosion
        weight_explosion_events = [
            e for e in events if e.event_type == InstabilityType.WEIGHT_EXPLOSION
        ]

        if weight_explosion_events:
            return True

        return False

    def record_reset(self, epoch: int, reason: str):
        """Record a training reset."""
        self.total_resets += 1
        self.last_reset_epoch = epoch

        logger.info(f"Training reset #{self.total_resets} at epoch {epoch}: {reason}")

    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            "total_events": len(self.instability_events),
            "total_resets": self.total_resets,
            "last_reset_epoch": self.last_reset_epoch,
            "sample_count": self.sample_count,
            "loss_ema": self.loss_ema,
            "gradient_norm_ema": self.gradient_norm_ema,
            "validation_loss_history": self.validation_loss_history[-10:],  # Last 10
            "events_by_type": {
                event_type.value: len(
                    [e for e in self.instability_events if e.event_type == event_type]
                )
                for event_type in InstabilityType
            },
            "events_by_severity": {
                severity: len(
                    [e for e in self.instability_events if e.severity == severity]
                )
                for severity in ["low", "medium", "high", "critical"]
            },
        }

    def reset_state(self):
        """Reset monitoring state (called after model reset)."""
        self.loss_ema = None
        self.gradient_norm_ema = None
        self.validation_loss_history = []
        self.sample_count = 0

        logger.info("Instability monitor state reset")
