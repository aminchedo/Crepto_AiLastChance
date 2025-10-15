"""
Advanced Learning Rate Scheduling
Implements warmup, cosine annealing, and hybrid schedulers for stable training
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import tensorflow as tf
from tensorflow import keras

logger = logging.getLogger(__name__)


class SchedulerType(Enum):
    """Types of learning rate schedulers."""

    WARMUP_COSINE = "warmup_cosine"
    WARMUP_PLATEAU = "warmup_plateau"
    HYBRID = "hybrid"
    COSINE_RESTART = "cosine_restart"
    ONE_CYCLE = "one_cycle"


@dataclass
class SchedulerConfig:
    """Configuration for learning rate scheduler."""

    scheduler_type: SchedulerType
    initial_lr: float
    warmup_steps: int
    total_steps: int
    min_lr: float = 1e-6
    max_lr: Optional[float] = None
    cosine_restart_period: Optional[int] = None
    plateau_patience: int = 10
    plateau_factor: float = 0.5
    plateau_min_lr: float = 1e-6
    plateau_monitor: str = "val_loss"
    plateau_mode: str = "min"


class WarmupCosineScheduler(keras.callbacks.Callback):
    """
    Learning rate scheduler with warmup followed by cosine annealing.

    Implements:
    1. Linear warmup from 0 to initial_lr over warmup_steps
    2. Cosine annealing from initial_lr to min_lr over remaining steps
    """

    def __init__(
        self,
        initial_lr: float,
        warmup_steps: int,
        total_steps: int,
        min_lr: float = 1e-6,
        verbose: bool = True,
    ):
        """
        Initialize warmup cosine scheduler.

        Args:
            initial_lr: Target learning rate after warmup
            warmup_steps: Number of steps for warmup
            total_steps: Total number of training steps
            min_lr: Minimum learning rate for cosine annealing
            verbose: Whether to log learning rate changes
        """
        super().__init__()
        self.initial_lr = initial_lr
        self.warmup_steps = warmup_steps
        self.total_steps = total_steps
        self.min_lr = min_lr
        self.verbose = verbose

        self.current_step = 0
        self.current_lr = 0.0

        logger.info(
            f"WarmupCosineScheduler: initial_lr={initial_lr}, "
            f"warmup_steps={warmup_steps}, total_steps={total_steps}, min_lr={min_lr}"
        )

    def on_train_batch_begin(self, batch, logs=None):
        """Update learning rate at the beginning of each batch."""
        if self.current_step < self.warmup_steps:
            # Warmup phase: linear increase from 0 to initial_lr
            self.current_lr = self.initial_lr * (self.current_step / self.warmup_steps)
        else:
            # Cosine annealing phase
            progress = (self.current_step - self.warmup_steps) / (
                self.total_steps - self.warmup_steps
            )
            progress = min(progress, 1.0)  # Clamp to [0, 1]

            # Cosine annealing formula
            self.current_lr = self.min_lr + (self.initial_lr - self.min_lr) * 0.5 * (
                1 + np.cos(np.pi * progress)
            )

        # Update optimizer learning rate
        if hasattr(self.model.optimizer, "learning_rate"):
            self.model.optimizer.learning_rate.assign(self.current_lr)

        self.current_step += 1

        if self.verbose and self.current_step % 100 == 0:
            logger.debug(f"Step {self.current_step}: lr = {self.current_lr:.8f}")

    def get_lr(self) -> float:
        """Get current learning rate."""
        return self.current_lr

    def get_config(self):
        """Get scheduler configuration."""
        return {
            "initial_lr": self.initial_lr,
            "warmup_steps": self.warmup_steps,
            "total_steps": self.total_steps,
            "min_lr": self.min_lr,
            "verbose": self.verbose,
        }


class CosineRestartScheduler(keras.callbacks.Callback):
    """
    Cosine annealing with restarts.

    Implements cosine annealing with periodic restarts to escape local minima.
    """

    def __init__(
        self,
        initial_lr: float,
        restart_period: int,
        min_lr: float = 1e-6,
        restart_factor: float = 1.0,
        verbose: bool = True,
    ):
        """
        Initialize cosine restart scheduler.

        Args:
            initial_lr: Initial learning rate
            restart_period: Number of steps between restarts
            min_lr: Minimum learning rate
            restart_factor: Factor to multiply initial_lr after restart
            verbose: Whether to log learning rate changes
        """
        super().__init__()
        self.initial_lr = initial_lr
        self.restart_period = restart_period
        self.min_lr = min_lr
        self.restart_factor = restart_factor
        self.verbose = verbose

        self.current_step = 0
        self.current_lr = initial_lr
        self.restart_count = 0

    def on_train_batch_begin(self, batch, logs=None):
        """Update learning rate at the beginning of each batch."""
        # Calculate position within current restart cycle
        cycle_position = self.current_step % self.restart_period
        cycle_progress = cycle_position / self.restart_period

        # Current cycle's maximum learning rate
        cycle_max_lr = self.initial_lr * (self.restart_factor**self.restart_count)

        # Cosine annealing within current cycle
        self.current_lr = self.min_lr + (cycle_max_lr - self.min_lr) * 0.5 * (
            1 + np.cos(np.pi * cycle_progress)
        )

        # Update optimizer learning rate
        if hasattr(self.model.optimizer, "learning_rate"):
            self.model.optimizer.learning_rate.assign(self.current_lr)

        # Check for restart
        if cycle_position == 0 and self.current_step > 0:
            self.restart_count += 1
            if self.verbose:
                logger.info(
                    f"Cosine restart #{self.restart_count} at step {self.current_step}"
                )

        self.current_step += 1

    def get_lr(self) -> float:
        """Get current learning rate."""
        return self.current_lr

    def get_config(self):
        """Get scheduler configuration."""
        return {
            "initial_lr": self.initial_lr,
            "restart_period": self.restart_period,
            "min_lr": self.min_lr,
            "restart_factor": self.restart_factor,
            "verbose": self.verbose,
        }


class HybridScheduler(keras.callbacks.Callback):
    """
    Hybrid scheduler combining warmup, cosine annealing, and ReduceLROnPlateau.

    Phase 1: Linear warmup
    Phase 2: Cosine annealing
    Phase 3: ReduceLROnPlateau (if validation doesn't improve)
    """

    def __init__(
        self,
        initial_lr: float,
        warmup_steps: int,
        cosine_steps: int,
        min_lr: float = 1e-6,
        plateau_patience: int = 10,
        plateau_factor: float = 0.5,
        plateau_monitor: str = "val_loss",
        plateau_mode: str = "min",
        verbose: bool = True,
    ):
        """
        Initialize hybrid scheduler.

        Args:
            initial_lr: Target learning rate after warmup
            warmup_steps: Number of warmup steps
            cosine_steps: Number of cosine annealing steps
            min_lr: Minimum learning rate
            plateau_patience: Patience for ReduceLROnPlateau
            plateau_factor: Factor for ReduceLROnPlateau
            plateau_monitor: Metric to monitor for plateau
            plateau_mode: "min" or "max" for plateau detection
            verbose: Whether to log learning rate changes
        """
        super().__init__()
        self.initial_lr = initial_lr
        self.warmup_steps = warmup_steps
        self.cosine_steps = cosine_steps
        self.min_lr = min_lr
        self.plateau_patience = plateau_patience
        self.plateau_factor = plateau_factor
        self.plateau_monitor = plateau_monitor
        self.plateau_mode = plateau_mode
        self.verbose = verbose

        # State tracking
        self.current_step = 0
        self.current_lr = 0.0
        self.phase = "warmup"  # "warmup", "cosine", "plateau"

        # Plateau detection
        self.best_metric = float("inf") if plateau_mode == "min" else float("-inf")
        self.plateau_wait = 0
        self.plateau_lr = initial_lr

        logger.info(
            f"HybridScheduler: initial_lr={initial_lr}, warmup_steps={warmup_steps}, "
            f"cosine_steps={cosine_steps}, plateau_patience={plateau_patience}"
        )

    def on_train_batch_begin(self, batch, logs=None):
        """Update learning rate at the beginning of each batch."""
        if self.phase == "warmup":
            if self.current_step < self.warmup_steps:
                # Linear warmup
                self.current_lr = self.initial_lr * (
                    self.current_step / self.warmup_steps
                )
            else:
                # Transition to cosine phase
                self.phase = "cosine"
                self.current_lr = self.initial_lr

        elif self.phase == "cosine":
            if self.current_step < self.warmup_steps + self.cosine_steps:
                # Cosine annealing
                progress = (self.current_step - self.warmup_steps) / self.cosine_steps
                progress = min(progress, 1.0)

                self.current_lr = self.min_lr + (
                    self.initial_lr - self.min_lr
                ) * 0.5 * (1 + np.cos(np.pi * progress))
            else:
                # Transition to plateau phase
                self.phase = "plateau"
                self.current_lr = self.min_lr
                self.plateau_lr = self.min_lr
                if self.verbose:
                    logger.info(
                        f"Transitioned to plateau phase at step {self.current_step}"
                    )

        elif self.phase == "plateau":
            # Plateau phase - learning rate managed by on_epoch_end
            pass

        # Update optimizer learning rate
        if hasattr(self.model.optimizer, "learning_rate"):
            self.model.optimizer.learning_rate.assign(self.current_lr)

        self.current_step += 1

    def on_epoch_end(self, epoch, logs=None):
        """Handle plateau detection at the end of each epoch."""
        if self.phase != "plateau":
            return

        # Get current metric value
        current_metric = logs.get(self.plateau_monitor)
        if current_metric is None:
            return

        # Check if metric improved
        is_better = (
            self.plateau_mode == "min" and current_metric < self.best_metric
        ) or (self.plateau_mode == "max" and current_metric > self.best_metric)

        if is_better:
            self.best_metric = current_metric
            self.plateau_wait = 0
        else:
            self.plateau_wait += 1

        # Reduce learning rate if plateau detected
        if self.plateau_wait >= self.plateau_patience:
            self.plateau_lr *= self.plateau_factor
            self.plateau_lr = max(self.plateau_lr, self.min_lr)
            self.plateau_wait = 0

            if self.verbose:
                logger.info(
                    f"Plateau detected: reducing LR to {self.plateau_lr:.8f} "
                    f"(epoch {epoch}, {self.plateau_monitor}={current_metric:.6f})"
                )

        # Update current learning rate
        self.current_lr = self.plateau_lr
        if hasattr(self.model.optimizer, "learning_rate"):
            self.model.optimizer.learning_rate.assign(self.current_lr)

    def get_lr(self) -> float:
        """Get current learning rate."""
        return self.current_lr

    def get_phase(self) -> str:
        """Get current phase."""
        return self.phase

    def get_config(self):
        """Get scheduler configuration."""
        return {
            "initial_lr": self.initial_lr,
            "warmup_steps": self.warmup_steps,
            "cosine_steps": self.cosine_steps,
            "min_lr": self.min_lr,
            "plateau_patience": self.plateau_patience,
            "plateau_factor": self.plateau_factor,
            "plateau_monitor": self.plateau_monitor,
            "plateau_mode": self.plateau_mode,
            "verbose": self.verbose,
        }


class OneCycleScheduler(keras.callbacks.Callback):
    """
    One Cycle Learning Rate Policy.

    Implements the one cycle policy with super-convergence:
    1. Linear increase from min_lr to max_lr
    2. Linear decrease from max_lr to min_lr
    3. Final linear decrease to min_lr/10
    """

    def __init__(
        self,
        max_lr: float,
        total_steps: int,
        min_lr: Optional[float] = None,
        pct_start: float = 0.3,
        pct_final: float = 0.1,
        verbose: bool = True,
    ):
        """
        Initialize one cycle scheduler.

        Args:
            max_lr: Maximum learning rate
            total_steps: Total number of training steps
            min_lr: Minimum learning rate (default: max_lr/10)
            pct_start: Percentage of steps for increasing phase
            pct_final: Percentage of steps for final decreasing phase
            verbose: Whether to log learning rate changes
        """
        super().__init__()
        self.max_lr = max_lr
        self.total_steps = total_steps
        self.min_lr = min_lr or max_lr / 10
        self.pct_start = pct_start
        self.pct_final = pct_final
        self.verbose = verbose

        # Calculate phase boundaries
        self.phase1_steps = int(total_steps * pct_start)
        self.phase2_steps = int(total_steps * (1 - pct_final))
        self.phase3_steps = total_steps

        self.current_step = 0
        self.current_lr = self.min_lr

        logger.info(
            f"OneCycleScheduler: max_lr={max_lr}, total_steps={total_steps}, "
            f"min_lr={self.min_lr}, pct_start={pct_start}, pct_final={pct_final}"
        )

    def on_train_batch_begin(self, batch, logs=None):
        """Update learning rate at the beginning of each batch."""
        if self.current_step < self.phase1_steps:
            # Phase 1: Linear increase from min_lr to max_lr
            progress = self.current_step / self.phase1_steps
            self.current_lr = self.min_lr + (self.max_lr - self.min_lr) * progress

        elif self.current_step < self.phase2_steps:
            # Phase 2: Linear decrease from max_lr to min_lr
            progress = (self.current_step - self.phase1_steps) / (
                self.phase2_steps - self.phase1_steps
            )
            self.current_lr = self.max_lr - (self.max_lr - self.min_lr) * progress

        else:
            # Phase 3: Linear decrease from min_lr to min_lr/10
            progress = (self.current_step - self.phase2_steps) / (
                self.phase3_steps - self.phase2_steps
            )
            final_lr = self.min_lr / 10
            self.current_lr = self.min_lr - (self.min_lr - final_lr) * progress

        # Update optimizer learning rate
        if hasattr(self.model.optimizer, "learning_rate"):
            self.model.optimizer.learning_rate.assign(self.current_lr)

        self.current_step += 1

    def get_lr(self) -> float:
        """Get current learning rate."""
        return self.current_lr

    def get_config(self):
        """Get scheduler configuration."""
        return {
            "max_lr": self.max_lr,
            "total_steps": self.total_steps,
            "min_lr": self.min_lr,
            "pct_start": self.pct_start,
            "pct_final": self.pct_final,
            "verbose": self.verbose,
        }


def get_scheduler(
    config: SchedulerConfig, verbose: bool = True
) -> keras.callbacks.Callback:
    """
    Factory function to create learning rate scheduler.

    Args:
        config: Scheduler configuration
        verbose: Whether to log learning rate changes

    Returns:
        Configured scheduler callback
    """
    if config.scheduler_type == SchedulerType.WARMUP_COSINE:
        return WarmupCosineScheduler(
            initial_lr=config.initial_lr,
            warmup_steps=config.warmup_steps,
            total_steps=config.total_steps,
            min_lr=config.min_lr,
            verbose=verbose,
        )

    elif config.scheduler_type == SchedulerType.COSINE_RESTART:
        return CosineRestartScheduler(
            initial_lr=config.initial_lr,
            restart_period=config.cosine_restart_period or 1000,
            min_lr=config.min_lr,
            verbose=verbose,
        )

    elif config.scheduler_type == SchedulerType.HYBRID:
        return HybridScheduler(
            initial_lr=config.initial_lr,
            warmup_steps=config.warmup_steps,
            cosine_steps=config.total_steps - config.warmup_steps,
            min_lr=config.min_lr,
            plateau_patience=config.plateau_patience,
            plateau_factor=config.plateau_factor,
            plateau_monitor=config.plateau_monitor,
            plateau_mode=config.plateau_mode,
            verbose=verbose,
        )

    elif config.scheduler_type == SchedulerType.ONE_CYCLE:
        return OneCycleScheduler(
            max_lr=config.max_lr or config.initial_lr,
            total_steps=config.total_steps,
            min_lr=config.min_lr,
            verbose=verbose,
        )

    else:
        raise ValueError(f"Unknown scheduler type: {config.scheduler_type}")


def create_default_scheduler(
    initial_lr: float, total_steps: int, scheduler_type: str = "hybrid", **kwargs
) -> keras.callbacks.Callback:
    """
    Create a default scheduler with sensible parameters.

    Args:
        initial_lr: Initial learning rate
        total_steps: Total number of training steps
        scheduler_type: Type of scheduler ("hybrid", "warmup_cosine", "one_cycle")
        **kwargs: Additional scheduler parameters

    Returns:
        Configured scheduler callback
    """
    # Default parameters
    warmup_steps = kwargs.get("warmup_steps", min(1000, total_steps // 10))
    min_lr = kwargs.get("min_lr", initial_lr / 100)

    if scheduler_type == "hybrid":
        config = SchedulerConfig(
            scheduler_type=SchedulerType.HYBRID,
            initial_lr=initial_lr,
            warmup_steps=warmup_steps,
            total_steps=total_steps,
            min_lr=min_lr,
            plateau_patience=kwargs.get("plateau_patience", 10),
            plateau_factor=kwargs.get("plateau_factor", 0.5),
            plateau_monitor=kwargs.get("plateau_monitor", "val_loss"),
            plateau_mode=kwargs.get("plateau_mode", "min"),
        )

    elif scheduler_type == "warmup_cosine":
        config = SchedulerConfig(
            scheduler_type=SchedulerType.WARMUP_COSINE,
            initial_lr=initial_lr,
            warmup_steps=warmup_steps,
            total_steps=total_steps,
            min_lr=min_lr,
        )

    elif scheduler_type == "one_cycle":
        config = SchedulerConfig(
            scheduler_type=SchedulerType.ONE_CYCLE,
            initial_lr=initial_lr,
            total_steps=total_steps,
            min_lr=min_lr,
            max_lr=kwargs.get("max_lr", initial_lr * 10),
        )

    else:
        raise ValueError(f"Unknown scheduler type: {scheduler_type}")

    return get_scheduler(config, verbose=kwargs.get("verbose", True))
