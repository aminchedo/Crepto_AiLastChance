"""
Custom Optimizers with Gradient Clipping and Enhanced Stability
Implements AdamW with proper weight decay and gradient norm tracking
"""

import logging
from typing import Any, Dict, Optional

import numpy as np
import tensorflow as tf
from tensorflow import keras

logger = logging.getLogger(__name__)


class AdamWOptimizer(keras.optimizers.Optimizer):
    """
    AdamW optimizer with decoupled weight decay.

    AdamW improves upon Adam by decoupling weight decay from the gradient update,
    leading to better generalization and training stability.

    Reference: Decoupled Weight Decay Regularization (Loshchilov & Hutter, 2019)
    """

    def __init__(
        self,
        learning_rate: float = 0.001,
        beta_1: float = 0.9,
        beta_2: float = 0.999,
        epsilon: float = 1e-7,
        weight_decay: float = 0.01,
        amsgrad: bool = False,
        clipnorm: Optional[float] = None,
        clipvalue: Optional[float] = None,
        name: str = "AdamW",
        **kwargs,
    ):
        """
        Initialize AdamW optimizer.

        Args:
            learning_rate: Learning rate
            beta_1: Exponential decay rate for 1st moment estimates
            beta_2: Exponential decay rate for 2nd moment estimates
            epsilon: Small constant for numerical stability
            weight_decay: Weight decay coefficient (L2 penalty)
            amsgrad: Use AMSGrad variant
            clipnorm: Gradient norm clipping value
            clipvalue: Gradient value clipping value
            name: Optimizer name
        """
        super().__init__(name=name, **kwargs)

        self._learning_rate = learning_rate
        self.beta_1 = beta_1
        self.beta_2 = beta_2
        self.epsilon = epsilon
        self.weight_decay = weight_decay
        self.amsgrad = amsgrad
        self.clipnorm = clipnorm
        self.clipvalue = clipvalue

        # Initialize gradient norm tracker
        self.gradient_norms = []
        self.gradient_norm_metric = keras.metrics.Mean(name="gradient_norm")

        logger.info(
            f"AdamW initialized: lr={learning_rate}, weight_decay={weight_decay}, "
            f"clipnorm={clipnorm}, clipvalue={clipvalue}"
        )

    def build(self, var_list):
        """Build optimizer variables."""
        super().build(var_list)

        if hasattr(self, "_built") and self._built:
            return

        self._built = True
        self._momentums = []
        self._velocities = []

        if self.amsgrad:
            self._vhats = []

        for var in var_list:
            self._momentums.append(
                self.add_variable_from_reference(model_variable=var, variable_name="m")
            )
            self._velocities.append(
                self.add_variable_from_reference(model_variable=var, variable_name="v")
            )
            if self.amsgrad:
                self._vhats.append(
                    self.add_variable_from_reference(
                        model_variable=var, variable_name="vhat"
                    )
                )

    def update_step(self, gradient, variable):
        """Perform a single optimization step."""
        lr = tf.cast(self.learning_rate, variable.dtype)
        local_step = tf.cast(self.iterations + 1, variable.dtype)
        beta_1_t = tf.cast(self.beta_1, variable.dtype)
        beta_2_t = tf.cast(self.beta_2, variable.dtype)

        # Get variable index
        var_key = self._var_key(variable)
        m = self._momentums[self._index_dict[var_key]]
        v = self._velocities[self._index_dict[var_key]]

        # Gradient clipping
        if self.clipnorm is not None:
            gradient = tf.clip_by_norm(gradient, self.clipnorm)
        if self.clipvalue is not None:
            gradient = tf.clip_by_value(gradient, -self.clipvalue, self.clipvalue)

        # Update biased first moment estimate
        m.assign(beta_1_t * m + (1 - beta_1_t) * gradient)

        # Update biased second moment estimate
        v.assign(beta_2_t * v + (1 - beta_2_t) * tf.square(gradient))

        if self.amsgrad:
            vhat = self._vhats[self._index_dict[var_key]]
            vhat.assign(tf.maximum(vhat, v))
            v_t = vhat
        else:
            v_t = v

        # Bias correction
        m_hat = m / (1 - tf.pow(beta_1_t, local_step))
        v_hat = v_t / (1 - tf.pow(beta_2_t, local_step))

        # Update variable with AdamW weight decay
        # AdamW: θ_t = θ_{t-1} - lr * (m_hat / (sqrt(v_hat) + ε) + λ * θ_{t-1})
        update = m_hat / (tf.sqrt(v_hat) + self.epsilon)

        # Apply weight decay directly to weights (decoupled from gradient)
        if self.weight_decay > 0:
            variable.assign(variable - lr * self.weight_decay * variable)

        # Apply gradient update
        variable.assign_sub(lr * update)

    def get_config(self):
        """Get optimizer configuration."""
        config = super().get_config()
        config.update(
            {
                "learning_rate": self._learning_rate,
                "beta_1": self.beta_1,
                "beta_2": self.beta_2,
                "epsilon": self.epsilon,
                "weight_decay": self.weight_decay,
                "amsgrad": self.amsgrad,
                "clipnorm": self.clipnorm,
                "clipvalue": self.clipvalue,
            }
        )
        return config


class GradientClipperCallback(keras.callbacks.Callback):
    """
    Callback to track and log gradient norms during training.
    Detects gradient explosions and provides diagnostic information.
    """

    def __init__(
        self,
        max_norm: float = 1.0,
        log_frequency: int = 100,
        alert_threshold: float = 10.0,
    ):
        """
        Initialize gradient clipper callback.

        Args:
            max_norm: Maximum gradient norm (for reference)
            log_frequency: How often to log gradient norms
            alert_threshold: Threshold for gradient explosion alerts
        """
        super().__init__()
        self.max_norm = max_norm
        self.log_frequency = log_frequency
        self.alert_threshold = alert_threshold

        self.gradient_norms = []
        self.step_count = 0

    def on_train_batch_end(self, batch, logs=None):
        """Track gradients after each batch."""
        self.step_count += 1

        # Get current gradient norm from optimizer if available
        if hasattr(self.model.optimizer, "gradient_norm_metric"):
            current_norm = self.model.optimizer.gradient_norm_metric.result().numpy()
            self.gradient_norms.append(current_norm)

            # Alert on gradient explosion
            if current_norm > self.alert_threshold:
                logger.warning(
                    f"Gradient explosion detected! Norm: {current_norm:.2f} "
                    f"(threshold: {self.alert_threshold})"
                )

            # Periodic logging
            if self.step_count % self.log_frequency == 0:
                recent_norms = self.gradient_norms[-self.log_frequency :]
                avg_norm = np.mean(recent_norms)
                max_norm = np.max(recent_norms)

                logger.info(
                    f"Gradient stats (last {self.log_frequency} steps): "
                    f"avg={avg_norm:.4f}, max={max_norm:.4f}"
                )


def clip_gradients_global_norm(gradients, max_norm: float = 1.0) -> tuple:
    """
    Clip gradients by global norm.

    Args:
        gradients: List of gradient tensors
        max_norm: Maximum global norm

    Returns:
        Tuple of (clipped_gradients, global_norm)
    """
    # Compute global norm
    global_norm = tf.sqrt(
        tf.reduce_sum([tf.reduce_sum(tf.square(g)) for g in gradients if g is not None])
    )

    # Clip gradients
    clipped_gradients = []
    clip_ratio = max_norm / (global_norm + 1e-6)
    clip_ratio = tf.minimum(clip_ratio, 1.0)

    for g in gradients:
        if g is not None:
            clipped_gradients.append(g * clip_ratio)
        else:
            clipped_gradients.append(None)

    return clipped_gradients, global_norm


def get_optimizer(
    name: str = "adamw",
    learning_rate: float = 0.001,
    weight_decay: float = 0.01,
    gradient_clip_norm: Optional[float] = 1.0,
    **kwargs,
) -> keras.optimizers.Optimizer:
    """
    Factory function to get optimizer with gradient clipping.

    Args:
        name: Optimizer name ('adamw', 'adam', 'sgd', 'rmsprop')
        learning_rate: Learning rate
        weight_decay: Weight decay coefficient
        gradient_clip_norm: Global gradient norm clipping value
        **kwargs: Additional optimizer arguments

    Returns:
        Configured optimizer instance
    """
    name = name.lower()

    if name == "adamw":
        return AdamWOptimizer(
            learning_rate=learning_rate,
            weight_decay=weight_decay,
            clipnorm=gradient_clip_norm,
            **kwargs,
        )
    elif name == "adam":
        return keras.optimizers.Adam(
            learning_rate=learning_rate, clipnorm=gradient_clip_norm, **kwargs
        )
    elif name == "sgd":
        return keras.optimizers.SGD(
            learning_rate=learning_rate, clipnorm=gradient_clip_norm, **kwargs
        )
    elif name == "rmsprop":
        return keras.optimizers.RMSprop(
            learning_rate=learning_rate, clipnorm=gradient_clip_norm, **kwargs
        )
    else:
        raise ValueError(f"Unknown optimizer: {name}")
