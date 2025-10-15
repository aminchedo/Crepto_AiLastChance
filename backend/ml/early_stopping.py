"""
Early Stopping with Multi-Metric Monitoring
Implements sophisticated early stopping with walk-forward validation
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import tensorflow as tf
from tensorflow import keras

logger = logging.getLogger(__name__)


class EarlyStoppingMode(Enum):
    """Modes for early stopping."""

    MIN = "min"
    MAX = "max"
    AUTO = "auto"


@dataclass
class EarlyStoppingConfig:
    """Configuration for early stopping."""

    monitor: str = "val_loss"
    patience: int = 20
    min_delta: float = 1e-4
    mode: EarlyStoppingMode = EarlyStoppingMode.AUTO
    restore_best_weights: bool = True
    baseline: Optional[float] = None
    min_improvement: Optional[float] = None
    start_from_epoch: int = 0


class MultiMetricEarlyStopping(keras.callbacks.Callback):
    """
    Early stopping with support for multiple metrics and sophisticated monitoring.

    Features:
    - Multiple metric monitoring
    - Walk-forward validation for time-series
    - Custom stopping criteria
    - Best model restoration
    - Detailed logging and statistics
    """

    def __init__(
        self,
        configs: List[EarlyStoppingConfig],
        walk_forward: bool = False,
        walk_forward_window: int = 100,
        custom_stopping_fn: Optional[Callable] = None,
        verbose: bool = True,
    ):
        """
        Initialize multi-metric early stopping.

        Args:
            configs: List of early stopping configurations
            walk_forward: Whether to use walk-forward validation
            walk_forward_window: Window size for walk-forward validation
            custom_stopping_fn: Custom function to determine stopping
            verbose: Whether to log detailed information
        """
        super().__init__()
        self.configs = configs
        self.walk_forward = walk_forward
        self.walk_forward_window = walk_forward_window
        self.custom_stopping_fn = custom_stopping_fn
        self.verbose = verbose

        # State tracking for each metric
        self.metric_states = {}
        for config in configs:
            self.metric_states[config.monitor] = {
                "config": config,
                "best_value": (
                    float("inf")
                    if config.mode == EarlyStoppingMode.MIN
                    else float("-inf")
                ),
                "best_epoch": 0,
                "wait_count": 0,
                "history": [],
                "improvement_count": 0,
                "last_improvement_epoch": 0,
            }

        # Global state
        self.stopped_epoch = 0
        self.best_weights = None
        self.stopping_reason = None
        self.stopping_epoch = 0

        # Walk-forward validation
        self.walk_forward_history = []
        self.walk_forward_predictions = []

        logger.info(
            f"MultiMetricEarlyStopping initialized: {len(configs)} metrics, "
            f"walk_forward={walk_forward}, patience={[c.patience for c in configs]}"
        )

    def on_train_begin(self, logs=None):
        """Initialize at the start of training."""
        # Set mode to auto if needed
        for config in self.configs:
            if config.mode == EarlyStoppingMode.AUTO:
                if "loss" in config.monitor:
                    config.mode = EarlyStoppingMode.MIN
                elif "acc" in config.monitor or "r2" in config.monitor:
                    config.mode = EarlyStoppingMode.MAX
                else:
                    config.mode = EarlyStoppingMode.MIN

        # Initialize baseline values
        for config in self.configs:
            if config.baseline is not None:
                state = self.metric_states[config.monitor]
                state["best_value"] = config.baseline

        if self.verbose:
            logger.info("Early stopping monitoring started")

    def on_epoch_end(self, epoch, logs=None):
        """Check for early stopping at the end of each epoch."""
        if logs is None:
            logs = {}

        # Skip if before start_from_epoch
        if epoch < min(config.start_from_epoch for config in self.configs):
            return

        # Check each monitored metric
        should_stop = False
        stopping_reasons = []

        for config in self.configs:
            metric_name = config.monitor
            current_value = logs.get(metric_name)

            if current_value is None:
                if self.verbose:
                    logger.warning(f"Metric '{metric_name}' not found in logs")
                continue

            # Update metric state
            state = self.metric_states[metric_name]
            state["history"].append(current_value)

            # Check for improvement
            is_better = self._is_better(current_value, state["best_value"], config.mode)
            improvement = abs(current_value - state["best_value"])

            if is_better and improvement >= config.min_delta:
                # Improvement detected
                state["best_value"] = current_value
                state["best_epoch"] = epoch
                state["wait_count"] = 0
                state["improvement_count"] += 1
                state["last_improvement_epoch"] = epoch

                # Save best weights if requested
                if config.restore_best_weights:
                    self.best_weights = self.model.get_weights()

                if self.verbose:
                    logger.info(
                        f"Epoch {epoch}: {metric_name} improved from {state['best_value']:.6f} "
                        f"to {current_value:.6f} (improvement: {improvement:.6f})"
                    )
            else:
                # No improvement
                state["wait_count"] += 1

                if self.verbose and state["wait_count"] % 5 == 0:
                    logger.debug(
                        f"Epoch {epoch}: {metric_name} no improvement for {state['wait_count']} epochs "
                        f"(current: {current_value:.6f}, best: {state['best_value']:.6f})"
                    )

            # Check patience
            if state["wait_count"] >= config.patience:
                should_stop = True
                stopping_reasons.append(
                    f"{metric_name} patience exceeded ({config.patience} epochs)"
                )

            # Check baseline
            if config.baseline is not None:
                if (
                    config.mode == EarlyStoppingMode.MIN
                    and current_value > config.baseline
                ):
                    should_stop = True
                    stopping_reasons.append(
                        f"{metric_name} above baseline ({config.baseline})"
                    )
                elif (
                    config.mode == EarlyStoppingMode.MAX
                    and current_value < config.baseline
                ):
                    should_stop = True
                    stopping_reasons.append(
                        f"{metric_name} below baseline ({config.baseline})"
                    )

            # Check minimum improvement
            if config.min_improvement is not None:
                if improvement < config.min_improvement:
                    should_stop = True
                    stopping_reasons.append(
                        f"{metric_name} improvement too small ({improvement:.6f} < {config.min_improvement})"
                    )

        # Walk-forward validation check
        if self.walk_forward and should_stop:
            walk_forward_should_stop = self._check_walk_forward(epoch, logs)
            if not walk_forward_should_stop:
                should_stop = False
                stopping_reasons = []

        # Custom stopping function
        if self.custom_stopping_fn and not should_stop:
            custom_should_stop, custom_reason = self.custom_stopping_fn(
                epoch, logs, self.metric_states
            )
            if custom_should_stop:
                should_stop = True
                stopping_reasons.append(f"Custom: {custom_reason}")

        # Stop training if criteria met
        if should_stop:
            self.stopped_epoch = epoch
            self.stopping_reason = "; ".join(stopping_reasons)
            self.stopping_epoch = epoch

            # Restore best weights
            if self.best_weights is not None:
                self.model.set_weights(self.best_weights)
                if self.verbose:
                    logger.info("Restored best weights")

            if self.verbose:
                logger.info(
                    f"Early stopping triggered at epoch {epoch}: {self.stopping_reason}"
                )

            self.model.stop_training = True

    def _is_better(self, current: float, best: float, mode: EarlyStoppingMode) -> bool:
        """Check if current value is better than best value."""
        if mode == EarlyStoppingMode.MIN:
            return current < best
        elif mode == EarlyStoppingMode.MAX:
            return current > best
        else:
            return False

    def _check_walk_forward(self, epoch: int, logs: Dict[str, float]) -> bool:
        """
        Check walk-forward validation criteria.

        Args:
            epoch: Current epoch
            logs: Current epoch logs

        Returns:
            True if should stop, False otherwise
        """
        # This is a simplified walk-forward check
        # In practice, you would implement actual walk-forward validation

        if len(self.walk_forward_history) < self.walk_forward_window:
            return False

        # Check if recent performance is consistently poor
        recent_history = self.walk_forward_history[-self.walk_forward_window :]
        recent_mean = np.mean(recent_history)
        recent_std = np.std(recent_history)

        # Stop if performance is consistently poor with low variance
        if recent_mean > 0.8 and recent_std < 0.1:  # Example thresholds
            return True

        return False

    def on_train_end(self, logs=None):
        """Called when training ends."""
        if self.stopped_epoch > 0:
            if self.verbose:
                logger.info(f"Training stopped early at epoch {self.stopped_epoch}")
        else:
            if self.verbose:
                logger.info("Training completed without early stopping")

    def get_best_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get best metrics for each monitored metric."""
        best_metrics = {}
        for metric_name, state in self.metric_states.items():
            best_metrics[metric_name] = {
                "best_value": state["best_value"],
                "best_epoch": state["best_epoch"],
                "improvement_count": state["improvement_count"],
                "last_improvement_epoch": state["last_improvement_epoch"],
                "total_epochs": len(state["history"]),
            }
        return best_metrics

    def get_stats(self) -> Dict[str, Any]:
        """Get early stopping statistics."""
        return {
            "stopped_epoch": self.stopped_epoch,
            "stopping_reason": self.stopping_reason,
            "stopping_epoch": self.stopping_epoch,
            "best_metrics": self.get_best_metrics(),
            "total_configs": len(self.configs),
            "walk_forward_enabled": self.walk_forward,
            "walk_forward_window": self.walk_forward_window,
        }


class AdaptiveEarlyStopping(MultiMetricEarlyStopping):
    """
    Adaptive early stopping that adjusts patience based on training progress.

    Features:
    - Dynamic patience adjustment
    - Learning rate aware stopping
    - Plateau detection
    - Adaptive thresholds
    """

    def __init__(
        self,
        configs: List[EarlyStoppingConfig],
        adaptive_patience: bool = True,
        lr_aware: bool = True,
        plateau_detection: bool = True,
        **kwargs,
    ):
        """
        Initialize adaptive early stopping.

        Args:
            configs: List of early stopping configurations
            adaptive_patience: Whether to adjust patience dynamically
            lr_aware: Whether to consider learning rate in stopping decisions
            plateau_detection: Whether to detect plateaus
            **kwargs: Additional arguments for parent class
        """
        super().__init__(configs, **kwargs)
        self.adaptive_patience = adaptive_patience
        self.lr_aware = lr_aware
        self.plateau_detection = plateau_detection

        # Adaptive state
        self.original_patience = {config.monitor: config.patience for config in configs}
        self.plateau_history = {config.monitor: [] for config in configs}

        logger.info(
            f"AdaptiveEarlyStopping: adaptive_patience={adaptive_patience}, "
            f"lr_aware={lr_aware}, plateau_detection={plateau_detection}"
        )

    def on_epoch_end(self, epoch, logs=None):
        """Adaptive early stopping check."""
        if logs is None:
            logs = {}

        # Adjust patience based on training progress
        if self.adaptive_patience:
            self._adjust_patience(epoch, logs)

        # Check for plateaus
        if self.plateau_detection:
            self._detect_plateaus(epoch, logs)

        # Call parent early stopping logic
        super().on_epoch_end(epoch, logs)

    def _adjust_patience(self, epoch: int, logs: Dict[str, float]):
        """Adjust patience based on training progress."""
        for config in self.configs:
            metric_name = config.monitor
            state = self.metric_states[metric_name]

            # Increase patience if model is still improving
            if state["improvement_count"] > 0:
                recent_improvements = sum(
                    1
                    for i in range(
                        max(0, len(state["history"]) - 10), len(state["history"])
                    )
                    if i > 0
                    and self._is_better(
                        state["history"][i], state["history"][i - 1], config.mode
                    )
                )

                if recent_improvements > 3:  # Still improving
                    config.patience = min(
                        config.patience + 5, self.original_patience[metric_name] * 2
                    )
                elif recent_improvements == 0:  # Not improving
                    config.patience = max(
                        config.patience - 2, self.original_patience[metric_name] // 2
                    )

    def _detect_plateaus(self, epoch: int, logs: Dict[str, float]):
        """Detect plateaus in training metrics."""
        for config in self.configs:
            metric_name = config.monitor
            state = self.metric_states[metric_name]

            if len(state["history"]) < 20:
                continue

            # Check for plateau (no significant improvement for many epochs)
            recent_history = state["history"][-20:]
            recent_std = np.std(recent_history)
            recent_mean = np.mean(recent_history)

            # Plateau detected if low variance and no improvement
            if recent_std < 0.01 and state["wait_count"] > 10:
                if self.verbose:
                    logger.warning(
                        f"Plateau detected in {metric_name} at epoch {epoch}"
                    )

                # Reduce patience for plateau
                config.patience = max(config.patience - 5, 5)


def create_early_stopping(
    monitor: str = "val_loss",
    patience: int = 20,
    min_delta: float = 1e-4,
    mode: str = "auto",
    restore_best_weights: bool = True,
    additional_monitors: Optional[List[str]] = None,
    walk_forward: bool = False,
    adaptive: bool = False,
    **kwargs,
) -> keras.callbacks.Callback:
    """
    Factory function to create early stopping callback.

    Args:
        monitor: Primary metric to monitor
        patience: Number of epochs to wait before stopping
        min_delta: Minimum change to qualify as improvement
        mode: "min", "max", or "auto"
        restore_best_weights: Whether to restore best weights
        additional_monitors: Additional metrics to monitor
        walk_forward: Whether to use walk-forward validation
        adaptive: Whether to use adaptive early stopping
        **kwargs: Additional arguments

    Returns:
        Configured early stopping callback
    """
    # Create primary config
    configs = [
        EarlyStoppingConfig(
            monitor=monitor,
            patience=patience,
            min_delta=min_delta,
            mode=EarlyStoppingMode(mode) if mode != "auto" else EarlyStoppingMode.AUTO,
            restore_best_weights=restore_best_weights,
            **kwargs,
        )
    ]

    # Add additional monitors
    if additional_monitors:
        for additional_monitor in additional_monitors:
            configs.append(
                EarlyStoppingConfig(
                    monitor=additional_monitor,
                    patience=patience,
                    min_delta=min_delta,
                    mode=EarlyStoppingMode.AUTO,
                    restore_best_weights=restore_best_weights,
                    **kwargs,
                )
            )

    # Create appropriate callback
    if adaptive:
        return AdaptiveEarlyStopping(
            configs=configs, walk_forward=walk_forward, **kwargs
        )
    else:
        return MultiMetricEarlyStopping(
            configs=configs, walk_forward=walk_forward, **kwargs
        )
