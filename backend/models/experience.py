"""
Experience Model for Database Storage
Stores experience replay data with metadata and statistics
"""

import json
import pickle
from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np
from sqlalchemy import (Column, DateTime, Float, Index, Integer, LargeBinary,
                        Text)
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Experience(Base):
    """Experience model for storing replay buffer data."""

    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Experience data
    state = Column(LargeBinary, nullable=False)  # Serialized state array
    action = Column(Integer, nullable=False)
    reward = Column(Float, nullable=False)
    next_state = Column(LargeBinary, nullable=False)  # Serialized next state array
    priority = Column(Float, nullable=False, default=1.0)

    # Metadata
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    metadata = Column(Text)  # JSON string of additional metadata
    is_critical = Column(Integer, default=0)  # 0 = False, 1 = True

    # Statistics
    episode_id = Column(Integer, nullable=True)
    step_in_episode = Column(Integer, nullable=True)
    model_version = Column(Text, nullable=True)

    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_timestamp", "timestamp"),
        Index("idx_priority", "priority"),
        Index("idx_critical", "is_critical"),
        Index("idx_episode", "episode_id"),
        Index("idx_model_version", "model_version"),
    )

    def __init__(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        priority: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        is_critical: bool = False,
        episode_id: Optional[int] = None,
        step_in_episode: Optional[int] = None,
        model_version: Optional[str] = None,
    ):
        """
        Initialize experience record.

        Args:
            state: Current state array
            action: Action taken
            reward: Reward received
            next_state: Next state array
            priority: Priority value for sampling
            metadata: Additional metadata
            is_critical: Whether this is a critical event
            episode_id: Episode identifier
            step_in_episode: Step number within episode
            model_version: Model version that generated this experience
        """
        self.state = self._serialize_array(state)
        self.action = action
        self.reward = reward
        self.next_state = self._serialize_array(next_state)
        self.priority = priority
        self.metadata = json.dumps(metadata) if metadata else None
        self.is_critical = 1 if is_critical else 0
        self.episode_id = episode_id
        self.step_in_episode = step_in_episode
        self.model_version = model_version
        self.timestamp = datetime.utcnow()

    def _serialize_array(self, array: np.ndarray) -> bytes:
        """Serialize numpy array to bytes."""
        return pickle.dumps(array)

    def _deserialize_array(self, data: bytes) -> np.ndarray:
        """Deserialize bytes to numpy array."""
        return pickle.loads(data)

    def get_state(self) -> np.ndarray:
        """Get deserialized state array."""
        return self._deserialize_array(self.state)

    def get_next_state(self) -> np.ndarray:
        """Get deserialized next state array."""
        return self._deserialize_array(self.next_state)

    def get_metadata(self) -> Dict[str, Any]:
        """Get deserialized metadata."""
        if self.metadata:
            return json.loads(self.metadata)
        return {}

    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """Set metadata."""
        self.metadata = json.dumps(metadata)

    def is_critical_event(self) -> bool:
        """Check if this is a critical event."""
        return bool(self.is_critical)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "state": self.get_state().tolist(),
            "action": self.action,
            "reward": self.reward,
            "next_state": self.get_next_state().tolist(),
            "priority": self.priority,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.get_metadata(),
            "is_critical": self.is_critical_event(),
            "episode_id": self.episode_id,
            "step_in_episode": self.step_in_episode,
            "model_version": self.model_version,
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Experience(id={self.id}, action={self.action}, reward={self.reward:.4f}, "
            f"priority={self.priority:.4f}, critical={self.is_critical_event()})"
        )


class ExperienceStats(Base):
    """Statistics model for experience replay buffer."""

    __tablename__ = "experience_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Statistics
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    buffer_size = Column(Integer, nullable=False)
    total_added = Column(Integer, nullable=False)
    total_sampled = Column(Integer, nullable=False)
    critical_events = Column(Integer, nullable=False, default=0)
    boosted_samples = Column(Integer, nullable=False, default=0)

    # Priority statistics
    min_priority = Column(Float, nullable=True)
    max_priority = Column(Float, nullable=True)
    mean_priority = Column(Float, nullable=True)
    std_priority = Column(Float, nullable=True)
    median_priority = Column(Float, nullable=True)

    # Buffer configuration
    capacity = Column(Integer, nullable=False)
    alpha = Column(Float, nullable=False)
    beta = Column(Float, nullable=False)
    epsilon = Column(Float, nullable=False)

    # Model information
    model_version = Column(Text, nullable=True)
    training_epoch = Column(Integer, nullable=True)

    def __init__(
        self,
        buffer_size: int,
        total_added: int,
        total_sampled: int,
        critical_events: int = 0,
        boosted_samples: int = 0,
        priority_stats: Optional[Dict[str, float]] = None,
        capacity: int = 100000,
        alpha: float = 0.6,
        beta: float = 0.4,
        epsilon: float = 1e-6,
        model_version: Optional[str] = None,
        training_epoch: Optional[int] = None,
    ):
        """
        Initialize experience statistics.

        Args:
            buffer_size: Current buffer size
            total_added: Total experiences added
            total_sampled: Total experiences sampled
            critical_events: Number of critical events
            boosted_samples: Number of boosted samples
            priority_stats: Priority statistics dictionary
            capacity: Buffer capacity
            alpha: Prioritization exponent
            beta: Importance sampling weight
            epsilon: Small constant for priorities
            model_version: Model version
            training_epoch: Current training epoch
        """
        self.timestamp = datetime.utcnow()
        self.buffer_size = buffer_size
        self.total_added = total_added
        self.total_sampled = total_sampled
        self.critical_events = critical_events
        self.boosted_samples = boosted_samples

        # Priority statistics
        if priority_stats:
            self.min_priority = priority_stats.get("min_priority")
            self.max_priority = priority_stats.get("max_priority")
            self.mean_priority = priority_stats.get("mean_priority")
            self.std_priority = priority_stats.get("std_priority")
            self.median_priority = priority_stats.get("median_priority")

        # Buffer configuration
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.epsilon = epsilon

        # Model information
        self.model_version = model_version
        self.training_epoch = training_epoch

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "buffer_size": self.buffer_size,
            "total_added": self.total_added,
            "total_sampled": self.total_sampled,
            "critical_events": self.critical_events,
            "boosted_samples": self.boosted_samples,
            "priority_stats": {
                "min_priority": self.min_priority,
                "max_priority": self.max_priority,
                "mean_priority": self.mean_priority,
                "std_priority": self.std_priority,
                "median_priority": self.median_priority,
            },
            "buffer_config": {
                "capacity": self.capacity,
                "alpha": self.alpha,
                "beta": self.beta,
                "epsilon": self.epsilon,
            },
            "model_version": self.model_version,
            "training_epoch": self.training_epoch,
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ExperienceStats(id={self.id}, size={self.buffer_size}, "
            f"added={self.total_added}, sampled={self.total_sampled})"
        )
