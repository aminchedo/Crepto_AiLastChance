"""
Safe Activation Functions with Clipping for Numerical Stability
Prevents overflow/underflow and NaN propagation
"""

import logging
from typing import Optional

import numpy as np
import tensorflow as tf
from tensorflow import keras

logger = logging.getLogger(__name__)


class SafeActivations:
    """
    Collection of activation functions with built-in clipping for stability.
    All activations clip outputs to prevent extreme values that can cause NaN/Inf.
    """

    def __init__(
        self, clip_min: float = -50.0, clip_max: float = 50.0, leaky_alpha: float = 0.01
    ):
        """
        Initialize safe activation functions.

        Args:
            clip_min: Minimum value for clipping
            clip_max: Maximum value for clipping
            leaky_alpha: Alpha parameter for Leaky ReLU
        """
        self.clip_min = clip_min
        self.clip_max = clip_max
        self.leaky_alpha = leaky_alpha

        logger.info(
            f"Safe activations initialized with clipping bounds: [{clip_min}, {clip_max}]"
        )

    def leaky_relu(self, x: tf.Tensor, alpha: Optional[float] = None) -> tf.Tensor:
        """
        Leaky ReLU with clipping: f(x) = max(alpha*x, x)

        Args:
            x: Input tensor
            alpha: Negative slope (default: self.leaky_alpha)

        Returns:
            Activated tensor
        """
        alpha = alpha if alpha is not None else self.leaky_alpha

        # Clip input first to prevent extreme values
        x_clipped = tf.clip_by_value(x, self.clip_min, self.clip_max)

        # Apply leaky ReLU
        activated = tf.nn.leaky_relu(x_clipped, alpha=alpha)

        # Clip output for extra safety
        result = tf.clip_by_value(activated, self.clip_min, self.clip_max)

        return result

    def sigmoid(self, x: tf.Tensor) -> tf.Tensor:
        """
        Safe sigmoid with input clipping: f(x) = 1 / (1 + exp(-x))

        Args:
            x: Input tensor

        Returns:
            Activated tensor in range (0, 1)
        """
        # Clip input to prevent overflow in exp
        x_clipped = tf.clip_by_value(x, self.clip_min, self.clip_max)

        # Apply sigmoid
        result = tf.nn.sigmoid(x_clipped)

        # Sigmoid output is naturally bounded to (0, 1)
        return result

    def tanh(self, x: tf.Tensor) -> tf.Tensor:
        """
        Safe tanh with input clipping: f(x) = (exp(x) - exp(-x)) / (exp(x) + exp(-x))

        Args:
            x: Input tensor

        Returns:
            Activated tensor in range (-1, 1)
        """
        # Clip input to prevent overflow
        x_clipped = tf.clip_by_value(x, self.clip_min, self.clip_max)

        # Apply tanh
        result = tf.nn.tanh(x_clipped)

        # Tanh output is naturally bounded to (-1, 1)
        return result

    def relu(self, x: tf.Tensor) -> tf.Tensor:
        """
        Safe ReLU with output clipping: f(x) = max(0, x)

        Args:
            x: Input tensor

        Returns:
            Activated tensor
        """
        # Clip input
        x_clipped = tf.clip_by_value(x, self.clip_min, self.clip_max)

        # Apply ReLU
        activated = tf.nn.relu(x_clipped)

        # Clip output
        result = tf.clip_by_value(activated, 0, self.clip_max)

        return result

    def elu(self, x: tf.Tensor, alpha: float = 1.0) -> tf.Tensor:
        """
        Safe ELU with clipping: f(x) = x if x > 0 else alpha * (exp(x) - 1)

        Args:
            x: Input tensor
            alpha: Scale for negative inputs

        Returns:
            Activated tensor
        """
        # Clip input
        x_clipped = tf.clip_by_value(x, self.clip_min, self.clip_max)

        # Apply ELU
        activated = tf.nn.elu(x_clipped, alpha=alpha)

        # Clip output
        result = tf.clip_by_value(activated, self.clip_min, self.clip_max)

        return result

    def swish(self, x: tf.Tensor, beta: float = 1.0) -> tf.Tensor:
        """
        Safe Swish/SiLU activation: f(x) = x * sigmoid(beta * x)

        Args:
            x: Input tensor
            beta: Scaling factor

        Returns:
            Activated tensor
        """
        # Clip input
        x_clipped = tf.clip_by_value(x, self.clip_min, self.clip_max)

        # Apply swish
        sigmoid_val = tf.nn.sigmoid(beta * x_clipped)
        activated = x_clipped * sigmoid_val

        # Clip output
        result = tf.clip_by_value(activated, self.clip_min, self.clip_max)

        return result

    def gelu(self, x: tf.Tensor, approximate: bool = False) -> tf.Tensor:
        """
        Safe GELU activation: f(x) = x * Phi(x) where Phi is Gaussian CDF

        Args:
            x: Input tensor
            approximate: Use tanh approximation for speed

        Returns:
            Activated tensor
        """
        # Clip input
        x_clipped = tf.clip_by_value(x, self.clip_min, self.clip_max)

        # Apply GELU
        activated = tf.nn.gelu(x_clipped, approximate=approximate)

        # Clip output
        result = tf.clip_by_value(activated, self.clip_min, self.clip_max)

        return result


class SafeActivationLayer(keras.layers.Layer):
    """
    Keras layer wrapper for safe activations.
    Can be used as a standalone layer in Sequential or Functional API.
    """

    def __init__(
        self,
        activation: str = "leaky_relu",
        clip_min: float = -50.0,
        clip_max: float = 50.0,
        **kwargs,
    ):
        """
        Initialize safe activation layer.

        Args:
            activation: Activation function name
            clip_min: Minimum clipping value
            clip_max: Maximum clipping value
            **kwargs: Additional layer arguments
        """
        super().__init__(**kwargs)
        self.activation_name = activation
        self.clip_min = clip_min
        self.clip_max = clip_max

        self.safe_act = SafeActivations(clip_min=clip_min, clip_max=clip_max)

        # Map activation name to function
        self.activation_fn = {
            "leaky_relu": self.safe_act.leaky_relu,
            "sigmoid": self.safe_act.sigmoid,
            "tanh": self.safe_act.tanh,
            "relu": self.safe_act.relu,
            "elu": self.safe_act.elu,
            "swish": self.safe_act.swish,
            "gelu": self.safe_act.gelu,
        }.get(activation.lower())

        if self.activation_fn is None:
            raise ValueError(f"Unknown activation: {activation}")

    def call(self, inputs: tf.Tensor) -> tf.Tensor:
        """Apply safe activation."""
        return self.activation_fn(inputs)

    def get_config(self):
        """Get configuration for serialization."""
        config = super().get_config()
        config.update(
            {
                "activation": self.activation_name,
                "clip_min": self.clip_min,
                "clip_max": self.clip_max,
            }
        )
        return config


def get_activation(
    name: str, clip_min: float = -50.0, clip_max: float = 50.0, **kwargs
):
    """
    Factory function to get safe activation function or layer.

    Args:
        name: Activation name
        clip_min: Minimum clipping value
        clip_max: Maximum clipping value
        **kwargs: Additional arguments

    Returns:
        Activation function or layer
    """
    if name.lower() in [
        "leaky_relu",
        "sigmoid",
        "tanh",
        "relu",
        "elu",
        "swish",
        "gelu",
    ]:
        return SafeActivationLayer(
            activation=name, clip_min=clip_min, clip_max=clip_max, **kwargs
        )
    else:
        # Fallback to Keras built-in
        logger.warning(f"Using Keras built-in activation: {name} (no clipping)")
        return keras.layers.Activation(name)


def check_for_nan_inf(tensor: tf.Tensor, name: str = "tensor") -> bool:
    """
    Check if tensor contains NaN or Inf values.

    Args:
        tensor: Tensor to check
        name: Name for logging

    Returns:
        True if contains NaN/Inf, False otherwise
    """
    has_nan = tf.reduce_any(tf.math.is_nan(tensor))
    has_inf = tf.reduce_any(tf.math.is_inf(tensor))

    if has_nan or has_inf:
        logger.error(f"{name} contains NaN={has_nan.numpy()}, Inf={has_inf.numpy()}")
        return True

    return False
