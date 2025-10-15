"""
Prioritized Experience Replay Buffer
Implements circular buffer with prioritized sampling and importance sampling weights
"""

import logging
import os
import pickle
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Experience:
    """Single experience tuple for replay buffer."""

    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    priority: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize after creation."""
        if self.metadata is None:
            self.metadata = {}


class PrioritizedReplayBuffer:
    """
    Prioritized Experience Replay Buffer with importance sampling.

    Features:
    - Circular buffer with configurable capacity
    - Prioritized sampling based on TD error
    - Importance sampling weights for bias correction
    - Beta annealing schedule
    - Critical event boosting
    - Batch extraction with shuffle capability
    """

    def __init__(
        self,
        capacity: int = 100000,
        alpha: float = 0.6,
        beta_start: float = 0.4,
        beta_frames: int = 50000,
        epsilon: float = 1e-6,
        critical_boost: float = 2.0,
        compression: bool = True,
    ):
        """
        Initialize prioritized replay buffer.

        Args:
            capacity: Maximum number of experiences to store
            alpha: Prioritization exponent (0 = uniform, 1 = full prioritization)
            beta_start: Initial importance sampling weight
            beta_frames: Number of frames to anneal beta
            epsilon: Small constant to prevent zero priorities
            critical_boost: Multiplier for critical event priorities
            compression: Whether to compress stored experiences
        """
        self.capacity = capacity
        self.alpha = alpha
        self.beta_start = beta_start
        self.beta_frames = beta_frames
        self.epsilon = epsilon
        self.critical_boost = critical_boost
        self.compression = compression

        # Buffer storage
        self.buffer = []
        self.priorities = []
        self.indices = []

        # State tracking
        self.size = 0
        self.write_index = 0
        self.total_added = 0
        self.total_sampled = 0

        # Beta annealing
        self.beta = beta_start
        self.beta_increment = (1.0 - beta_start) / beta_frames

        # Statistics
        self.critical_events = 0
        self.boosted_samples = 0

        logger.info(
            f"PrioritizedReplayBuffer initialized: capacity={capacity}, "
            f"alpha={alpha}, beta_start={beta_start}, beta_frames={beta_frames}"
        )

    def add(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        priority: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_critical: bool = False,
    ) -> None:
        """
        Add experience to buffer.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            priority: Priority value (if None, uses reward magnitude)
            metadata: Additional metadata
            is_critical: Whether this is a critical event
        """
        # Calculate priority if not provided
        if priority is None:
            priority = abs(reward) + self.epsilon

        # Boost priority for critical events
        if is_critical:
            priority *= self.critical_boost
            self.critical_events += 1

        # Create experience
        experience = Experience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            priority=priority,
            timestamp=datetime.now(),
            metadata=metadata or {},
        )

        # Add to buffer
        if self.size < self.capacity:
            # Buffer not full
            self.buffer.append(experience)
            self.priorities.append(priority)
            self.indices.append(self.total_added)
            self.size += 1
        else:
            # Buffer full, overwrite oldest
            self.buffer[self.write_index] = experience
            self.priorities[self.write_index] = priority
            self.indices[self.write_index] = self.total_added
            self.write_index = (self.write_index + 1) % self.capacity

        self.total_added += 1

        if is_critical:
            logger.debug(f"Critical experience added: priority={priority:.4f}")

    def sample(
        self, batch_size: int, shuffle: bool = True
    ) -> Tuple[List[Experience], np.ndarray, np.ndarray]:
        """
        Sample batch of experiences with importance sampling weights.

        Args:
            batch_size: Number of experiences to sample
            shuffle: Whether to shuffle the batch

        Returns:
            Tuple of (experiences, indices, importance_weights)
        """
        if self.size == 0:
            raise ValueError("Cannot sample from empty buffer")

        if batch_size > self.size:
            batch_size = self.size

        # Calculate sampling probabilities
        priorities = np.array(self.priorities[: self.size])
        probabilities = priorities**self.alpha
        probabilities /= probabilities.sum()

        # Sample indices
        indices = np.random.choice(
            self.size, size=batch_size, replace=False, p=probabilities
        )

        # Get experiences
        experiences = [self.buffer[i] for i in indices]

        # Calculate importance sampling weights
        importance_weights = self._calculate_importance_weights(indices, probabilities)

        # Shuffle if requested
        if shuffle:
            shuffle_indices = np.random.permutation(batch_size)
            experiences = [experiences[i] for i in shuffle_indices]
            indices = indices[shuffle_indices]
            importance_weights = importance_weights[shuffle_indices]

        self.total_sampled += batch_size

        return experiences, indices, importance_weights

    def _calculate_importance_weights(
        self, indices: np.ndarray, probabilities: np.ndarray
    ) -> np.ndarray:
        """Calculate importance sampling weights."""
        # Importance sampling weight = (1/N * 1/p) ** beta
        N = self.size
        p = probabilities[indices]

        # Avoid division by zero
        p = np.maximum(p, 1e-8)

        # Calculate weights
        weights = (1.0 / (N * p)) ** self.beta

        # Normalize weights
        weights = weights / weights.max()

        return weights

    def update_priorities(self, indices: np.ndarray, priorities: np.ndarray) -> None:
        """
        Update priorities for sampled experiences.

        Args:
            indices: Indices of experiences to update
            priorities: New priority values
        """
        for idx, priority in zip(indices, priorities):
            if idx < self.size:
                # Add epsilon to prevent zero priority
                new_priority = abs(priority) + self.epsilon
                self.priorities[idx] = new_priority

                # Update experience priority
                self.buffer[idx].priority = new_priority

    def update_beta(self, frame: int) -> None:
        """
        Update beta for importance sampling weight correction.

        Args:
            frame: Current frame number
        """
        if frame < self.beta_frames:
            self.beta = self.beta_start + frame * self.beta_increment
        else:
            self.beta = 1.0

    def boost_critical_events(
        self, indices: List[int], boost_factor: float = 2.0
    ) -> None:
        """
        Boost priorities for critical events.

        Args:
            indices: Indices of critical events
            boost_factor: Factor to boost priorities
        """
        for idx in indices:
            if idx < self.size:
                old_priority = self.priorities[idx]
                new_priority = old_priority * boost_factor
                self.priorities[idx] = new_priority
                self.buffer[idx].priority = new_priority
                self.boosted_samples += 1

        logger.debug(f"Boosted {len(indices)} critical events by factor {boost_factor}")

    def get_recent_experiences(
        self, count: int, shuffle: bool = True
    ) -> List[Experience]:
        """
        Get most recent experiences.

        Args:
            count: Number of recent experiences to return
            shuffle: Whether to shuffle the results

        Returns:
            List of recent experiences
        """
        if self.size == 0:
            return []

        count = min(count, self.size)

        if self.size < self.capacity:
            # Buffer not full, get last count experiences
            recent_experiences = self.buffer[-count:]
        else:
            # Buffer full, get experiences around write index
            start_idx = (self.write_index - count) % self.capacity
            if start_idx + count <= self.capacity:
                recent_experiences = self.buffer[start_idx : start_idx + count]
            else:
                recent_experiences = (
                    self.buffer[start_idx:]
                    + self.buffer[: count - (self.capacity - start_idx)]
                )

        if shuffle:
            random.shuffle(recent_experiences)

        return recent_experiences

    def get_priority_stats(self) -> Dict[str, float]:
        """Get priority statistics."""
        if self.size == 0:
            return {}

        priorities = np.array(self.priorities[: self.size])

        return {
            "min_priority": float(np.min(priorities)),
            "max_priority": float(np.max(priorities)),
            "mean_priority": float(np.mean(priorities)),
            "std_priority": float(np.std(priorities)),
            "median_priority": float(np.median(priorities)),
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics."""
        priority_stats = self.get_priority_stats()

        return {
            "size": self.size,
            "capacity": self.capacity,
            "total_added": self.total_added,
            "total_sampled": self.total_sampled,
            "critical_events": self.critical_events,
            "boosted_samples": self.boosted_samples,
            "beta": self.beta,
            "alpha": self.alpha,
            "write_index": self.write_index,
            "priority_stats": priority_stats,
            "utilization": self.size / self.capacity if self.capacity > 0 else 0.0,
        }

    def save(self, filepath: Union[str, Path]) -> bool:
        """
        Save buffer to disk.

        Args:
            filepath: Path to save buffer

        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Prepare data for saving
            save_data = {
                "buffer": self.buffer,
                "priorities": self.priorities,
                "indices": self.indices,
                "size": self.size,
                "write_index": self.write_index,
                "total_added": self.total_added,
                "total_sampled": self.total_sampled,
                "critical_events": self.critical_events,
                "boosted_samples": self.boosted_samples,
                "beta": self.beta,
                "config": {
                    "capacity": self.capacity,
                    "alpha": self.alpha,
                    "beta_start": self.beta_start,
                    "beta_frames": self.beta_frames,
                    "epsilon": self.epsilon,
                    "critical_boost": self.critical_boost,
                    "compression": self.compression,
                },
            }

            # Save with compression if enabled
            if self.compression:
                import gzip

                with gzip.open(filepath, "wb") as f:
                    pickle.dump(save_data, f)
            else:
                with open(filepath, "wb") as f:
                    pickle.dump(save_data, f)

            logger.info(f"Buffer saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save buffer: {e}")
            return False

    def load(self, filepath: Union[str, Path]) -> bool:
        """
        Load buffer from disk.

        Args:
            filepath: Path to load buffer from

        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = Path(filepath)

            if not filepath.exists():
                logger.error(f"Buffer file not found: {filepath}")
                return False

            # Load data
            if self.compression:
                import gzip

                with gzip.open(filepath, "rb") as f:
                    save_data = pickle.load(f)
            else:
                with open(filepath, "rb") as f:
                    save_data = pickle.load(f)

            # Restore buffer state
            self.buffer = save_data["buffer"]
            self.priorities = save_data["priorities"]
            self.indices = save_data["indices"]
            self.size = save_data["size"]
            self.write_index = save_data["write_index"]
            self.total_added = save_data["total_added"]
            self.total_sampled = save_data["total_sampled"]
            self.critical_events = save_data["critical_events"]
            self.boosted_samples = save_data["boosted_samples"]
            self.beta = save_data["beta"]

            # Restore config
            config = save_data["config"]
            self.capacity = config["capacity"]
            self.alpha = config["alpha"]
            self.beta_start = config["beta_start"]
            self.beta_frames = config["beta_frames"]
            self.epsilon = config["epsilon"]
            self.critical_boost = config["critical_boost"]
            self.compression = config["compression"]

            logger.info(f"Buffer loaded from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to load buffer: {e}")
            return False

    def clear(self) -> None:
        """Clear the buffer."""
        self.buffer.clear()
        self.priorities.clear()
        self.indices.clear()
        self.size = 0
        self.write_index = 0
        self.total_added = 0
        self.total_sampled = 0
        self.critical_events = 0
        self.boosted_samples = 0
        self.beta = self.beta_start

        logger.info("Buffer cleared")

    def __len__(self) -> int:
        """Return current buffer size."""
        return self.size

    def __repr__(self) -> str:
        """String representation of buffer."""
        return (
            f"PrioritizedReplayBuffer(size={self.size}, capacity={self.capacity}, "
            f"alpha={self.alpha}, beta={self.beta:.3f})"
        )
