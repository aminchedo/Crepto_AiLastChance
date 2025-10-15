"""
Xavier/Glorot Weight Initialization for Neural Network Stability
Implements uniform and normal variants with proper variance scaling
"""

import logging
from typing import Optional, Tuple

import numpy as np
import tensorflow as tf
from tensorflow import keras

logger = logging.getLogger(__name__)


class XavierInitializer:
    """
    Xavier/Glorot initialization for stable neural network training.

    Maintains variance across layers to prevent vanishing/exploding gradients.
    Xavier Uniform: W ~ U(-sqrt(6/(fan_in + fan_out)), sqrt(6/(fan_in + fan_out)))
    Xavier Normal: W ~ N(0, sqrt(2/(fan_in + fan_out)))
    """

    def __init__(self, seed: Optional[int] = None, distribution: str = "uniform"):
        """
        Initialize Xavier weight initializer.

        Args:
            seed: Random seed for reproducibility
            distribution: 'uniform' or 'normal'
        """
        self.seed = seed
        self.distribution = distribution.lower()

        if self.distribution not in ["uniform", "normal"]:
            raise ValueError(
                f"Distribution must be 'uniform' or 'normal', got {distribution}"
            )

        if seed is not None:
            np.random.seed(seed)
            tf.random.set_seed(seed)
            logger.info(f"Xavier initializer seed set to: {seed}")

    def uniform(self, shape: Tuple[int, ...], dtype=tf.float32) -> tf.Tensor:
        """
        Xavier uniform initialization.

        Args:
            shape: Shape of weight tensor (fan_in, fan_out)
            dtype: Data type

        Returns:
            Initialized weight tensor
        """
        if len(shape) < 2:
            raise ValueError(
                f"Xavier initialization requires at least 2D shape, got {shape}"
            )

        fan_in = shape[0]
        fan_out = shape[1]

        # Xavier uniform limit
        limit = np.sqrt(6.0 / (fan_in + fan_out))

        # Generate uniform random weights
        weights = np.random.uniform(-limit, limit, shape).astype(dtype.as_numpy_dtype)

        logger.debug(
            f"Xavier uniform initialized weights with shape {shape}, limit={limit:.4f}"
        )

        return tf.constant(weights, dtype=dtype)

    def normal(self, shape: Tuple[int, ...], dtype=tf.float32) -> tf.Tensor:
        """
        Xavier normal initialization.

        Args:
            shape: Shape of weight tensor (fan_in, fan_out)
            dtype: Data type

        Returns:
            Initialized weight tensor
        """
        if len(shape) < 2:
            raise ValueError(
                f"Xavier initialization requires at least 2D shape, got {shape}"
            )

        fan_in = shape[0]
        fan_out = shape[1]

        # Xavier normal standard deviation
        std = np.sqrt(2.0 / (fan_in + fan_out))

        # Generate normal random weights
        weights = np.random.normal(0, std, shape).astype(dtype.as_numpy_dtype)

        logger.debug(
            f"Xavier normal initialized weights with shape {shape}, std={std:.4f}"
        )

        return tf.constant(weights, dtype=dtype)

    def __call__(self, shape: Tuple[int, ...], dtype=tf.float32) -> tf.Tensor:
        """
        Call method for use as Keras initializer.

        Args:
            shape: Shape of weight tensor
            dtype: Data type

        Returns:
            Initialized weights
        """
        if self.distribution == "uniform":
            return self.uniform(shape, dtype)
        else:
            return self.normal(shape, dtype)

    def get_config(self):
        """Get configuration for serialization."""
        return {
            "seed": self.seed,
            "distribution": self.distribution,
        }


class HeInitializer:
    """
    He initialization for ReLU-based networks.
    Optimized for ReLU activations with higher variance than Xavier.
    """

    def __init__(self, seed: Optional[int] = None, distribution: str = "normal"):
        self.seed = seed
        self.distribution = distribution.lower()

        if seed is not None:
            np.random.seed(seed)
            tf.random.set_seed(seed)

    def uniform(self, shape: Tuple[int, ...], dtype=tf.float32) -> tf.Tensor:
        """He uniform initialization."""
        fan_in = shape[0]
        limit = np.sqrt(6.0 / fan_in)
        weights = np.random.uniform(-limit, limit, shape).astype(dtype.as_numpy_dtype)
        return tf.constant(weights, dtype=dtype)

    def normal(self, shape: Tuple[int, ...], dtype=tf.float32) -> tf.Tensor:
        """He normal initialization."""
        fan_in = shape[0]
        std = np.sqrt(2.0 / fan_in)
        weights = np.random.normal(0, std, shape).astype(dtype.as_numpy_dtype)
        return tf.constant(weights, dtype=dtype)

    def __call__(self, shape: Tuple[int, ...], dtype=tf.float32) -> tf.Tensor:
        if self.distribution == "uniform":
            return self.uniform(shape, dtype)
        else:
            return self.normal(shape, dtype)


def get_initializer(name: str, seed: Optional[int] = None, **kwargs):
    """
    Factory function to get weight initializer.

    Args:
        name: Initializer name ('xavier_uniform', 'xavier_normal', 'he_uniform', 'he_normal')
        seed: Random seed
        **kwargs: Additional arguments

    Returns:
        Initializer instance or Keras initializer
    """
    if name == "xavier_uniform":
        return XavierInitializer(seed=seed, distribution="uniform")
    elif name == "xavier_normal":
        return XavierInitializer(seed=seed, distribution="normal")
    elif name == "he_uniform":
        return HeInitializer(seed=seed, distribution="uniform")
    elif name == "he_normal":
        return HeInitializer(seed=seed, distribution="normal")
    elif name == "glorot_uniform":
        # Keras built-in (same as Xavier uniform)
        return keras.initializers.GlorotUniform(seed=seed)
    elif name == "glorot_normal":
        # Keras built-in (same as Xavier normal)
        return keras.initializers.GlorotNormal(seed=seed)
    else:
        raise ValueError(f"Unknown initializer: {name}")


# Validation function
def validate_initialization(
    weights: np.ndarray, expected_std: float, tolerance: float = 0.1
):
    """
    Validate that weights are properly initialized.

    Args:
        weights: Weight array to validate
        expected_std: Expected standard deviation
        tolerance: Acceptable deviation from expected std

    Returns:
        True if valid, False otherwise
    """
    actual_mean = np.mean(weights)
    actual_std = np.std(weights)

    mean_ok = abs(actual_mean) < tolerance
    std_ok = abs(actual_std - expected_std) < expected_std * tolerance

    logger.debug(
        f"Weight validation: mean={actual_mean:.6f} (expected ~0), "
        f"std={actual_std:.6f} (expected {expected_std:.6f})"
    )

    return mean_ok and std_ok
