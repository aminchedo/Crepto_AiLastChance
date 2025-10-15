"""
Exploration Strategies for Neural AI Agents
Implements epsilon-greedy, temperature-based softmax, and adaptive exploration
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import tensorflow as tf

logger = logging.getLogger(__name__)


class ExplorationType(Enum):
    """Types of exploration strategies."""

    EPSILON_GREEDY = "epsilon_greedy"
    TEMPERATURE_SOFTMAX = "temperature_softmax"
    UCB = "ucb"
    THOMPSON = "thompson"
    ADAPTIVE = "adaptive"


@dataclass
class ExplorationConfig:
    """Configuration for exploration strategy."""

    exploration_type: ExplorationType
    epsilon_start: float = 0.3
    epsilon_end: float = 0.01
    epsilon_decay: int = 50000
    temperature_start: float = 1.0
    temperature_end: float = 0.1
    temperature_decay: int = 50000
    ucb_c: float = 2.0
    thompson_alpha: float = 1.0
    thompson_beta: float = 1.0


class EpsilonGreedyExploration:
    """
    Epsilon-greedy exploration strategy.

    Features:
    - Linear and exponential decay schedules
    - Custom decay functions
    - Exploration statistics tracking
    - Adaptive epsilon adjustment
    """

    def __init__(
        self,
        epsilon_start: float = 0.3,
        epsilon_end: float = 0.01,
        epsilon_decay: int = 50000,
        decay_type: str = "linear",
        min_epsilon: float = 0.01,
    ):
        """
        Initialize epsilon-greedy exploration.

        Args:
            epsilon_start: Initial epsilon value
            epsilon_end: Final epsilon value
            epsilon_decay: Number of steps to decay epsilon
            decay_type: Type of decay ("linear", "exponential", "cosine")
            min_epsilon: Minimum epsilon value
        """
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.decay_type = decay_type
        self.min_epsilon = min_epsilon

        # State tracking
        self.current_step = 0
        self.current_epsilon = epsilon_start

        # Statistics
        self.exploration_count = 0
        self.exploitation_count = 0
        self.total_actions = 0

        logger.info(
            f"EpsilonGreedyExploration initialized: start={epsilon_start}, "
            f"end={epsilon_end}, decay={epsilon_decay}, type={decay_type}"
        )

    def get_epsilon(self, step: Optional[int] = None) -> float:
        """
        Get current epsilon value.

        Args:
            step: Current step (if None, uses internal counter)

        Returns:
            Current epsilon value
        """
        if step is not None:
            self.current_step = step

        if self.decay_type == "linear":
            # Linear decay
            progress = min(self.current_step / self.epsilon_decay, 1.0)
            self.current_epsilon = self.epsilon_start - progress * (
                self.epsilon_start - self.epsilon_end
            )

        elif self.decay_type == "exponential":
            # Exponential decay
            decay_rate = (
                np.log(self.epsilon_end / self.epsilon_start) / self.epsilon_decay
            )
            self.current_epsilon = self.epsilon_start * np.exp(
                decay_rate * self.current_step
            )

        elif self.decay_type == "cosine":
            # Cosine decay
            progress = min(self.current_step / self.epsilon_decay, 1.0)
            self.current_epsilon = self.epsilon_end + (
                self.epsilon_start - self.epsilon_end
            ) * 0.5 * (1 + np.cos(np.pi * progress))

        else:
            raise ValueError(f"Unknown decay type: {self.decay_type}")

        # Ensure minimum epsilon
        self.current_epsilon = max(self.current_epsilon, self.min_epsilon)

        return self.current_epsilon

    def should_explore(self, step: Optional[int] = None) -> bool:
        """
        Determine if should explore or exploit.

        Args:
            step: Current step

        Returns:
            True if should explore, False if should exploit
        """
        epsilon = self.get_epsilon(step)
        should_explore = np.random.random() < epsilon

        if should_explore:
            self.exploration_count += 1
        else:
            self.exploitation_count += 1

        self.total_actions += 1

        return should_explore

    def select_action(
        self, q_values: np.ndarray, step: Optional[int] = None
    ) -> Tuple[int, bool]:
        """
        Select action using epsilon-greedy strategy.

        Args:
            q_values: Q-values for each action
            step: Current step

        Returns:
            Tuple of (selected_action, is_exploration)
        """
        should_explore = self.should_explore(step)

        if should_explore:
            # Random action
            action = np.random.randint(len(q_values))
        else:
            # Greedy action
            action = np.argmax(q_values)

        return action, should_explore

    def update_step(self, step: int) -> None:
        """Update internal step counter."""
        self.current_step = step

    def get_stats(self) -> Dict[str, Any]:
        """Get exploration statistics."""
        exploration_ratio = self.exploration_count / max(self.total_actions, 1)

        return {
            "current_epsilon": self.current_epsilon,
            "current_step": self.current_step,
            "exploration_count": self.exploration_count,
            "exploitation_count": self.exploitation_count,
            "total_actions": self.total_actions,
            "exploration_ratio": exploration_ratio,
            "epsilon_start": self.epsilon_start,
            "epsilon_end": self.epsilon_end,
            "epsilon_decay": self.epsilon_decay,
            "decay_type": self.decay_type,
        }


class TemperatureSoftmaxExploration:
    """
    Temperature-based softmax exploration.

    Features:
    - Temperature annealing
    - Softmax action selection
    - Exploration probability tracking
    - Adaptive temperature adjustment
    """

    def __init__(
        self,
        temperature_start: float = 1.0,
        temperature_end: float = 0.1,
        temperature_decay: int = 50000,
        decay_type: str = "linear",
        min_temperature: float = 0.01,
    ):
        """
        Initialize temperature softmax exploration.

        Args:
            temperature_start: Initial temperature
            temperature_end: Final temperature
            temperature_decay: Number of steps to decay temperature
            decay_type: Type of decay ("linear", "exponential", "cosine")
            min_temperature: Minimum temperature value
        """
        self.temperature_start = temperature_start
        self.temperature_end = temperature_end
        self.temperature_decay = temperature_decay
        self.decay_type = decay_type
        self.min_temperature = min_temperature

        # State tracking
        self.current_step = 0
        self.current_temperature = temperature_start

        # Statistics
        self.action_counts = {}
        self.total_actions = 0

        logger.info(
            f"TemperatureSoftmaxExploration initialized: start={temperature_start}, "
            f"end={temperature_end}, decay={temperature_decay}, type={decay_type}"
        )

    def get_temperature(self, step: Optional[int] = None) -> float:
        """
        Get current temperature value.

        Args:
            step: Current step (if None, uses internal counter)

        Returns:
            Current temperature value
        """
        if step is not None:
            self.current_step = step

        if self.decay_type == "linear":
            # Linear decay
            progress = min(self.current_step / self.temperature_decay, 1.0)
            self.current_temperature = self.temperature_start - progress * (
                self.temperature_start - self.temperature_end
            )

        elif self.decay_type == "exponential":
            # Exponential decay
            decay_rate = (
                np.log(self.temperature_end / self.temperature_start)
                / self.temperature_decay
            )
            self.current_temperature = self.temperature_start * np.exp(
                decay_rate * self.current_step
            )

        elif self.decay_type == "cosine":
            # Cosine decay
            progress = min(self.current_step / self.temperature_decay, 1.0)
            self.current_temperature = self.temperature_end + (
                self.temperature_start - self.temperature_end
            ) * 0.5 * (1 + np.cos(np.pi * progress))

        else:
            raise ValueError(f"Unknown decay type: {self.decay_type}")

        # Ensure minimum temperature
        self.current_temperature = max(self.current_temperature, self.min_temperature)

        return self.current_temperature

    def select_action(
        self, q_values: np.ndarray, step: Optional[int] = None
    ) -> Tuple[int, float]:
        """
        Select action using temperature softmax.

        Args:
            q_values: Q-values for each action
            step: Current step

        Returns:
            Tuple of (selected_action, exploration_probability)
        """
        temperature = self.get_temperature(step)

        # Apply temperature scaling
        scaled_q_values = q_values / temperature

        # Softmax probabilities
        exp_values = np.exp(
            scaled_q_values - np.max(scaled_q_values)
        )  # Numerical stability
        probabilities = exp_values / np.sum(exp_values)

        # Sample action
        action = np.random.choice(len(q_values), p=probabilities)

        # Track statistics
        self.action_counts[action] = self.action_counts.get(action, 0) + 1
        self.total_actions += 1

        return action, probabilities[action]

    def get_action_probabilities(
        self, q_values: np.ndarray, step: Optional[int] = None
    ) -> np.ndarray:
        """
        Get action selection probabilities.

        Args:
            q_values: Q-values for each action
            step: Current step

        Returns:
            Action probabilities
        """
        temperature = self.get_temperature(step)

        # Apply temperature scaling
        scaled_q_values = q_values / temperature

        # Softmax probabilities
        exp_values = np.exp(
            scaled_q_values - np.max(scaled_q_values)
        )  # Numerical stability
        probabilities = exp_values / np.sum(exp_values)

        return probabilities

    def update_step(self, step: int) -> None:
        """Update internal step counter."""
        self.current_step = step

    def get_stats(self) -> Dict[str, Any]:
        """Get exploration statistics."""
        action_distribution = {
            action: count / max(self.total_actions, 1)
            for action, count in self.action_counts.items()
        }

        return {
            "current_temperature": self.current_temperature,
            "current_step": self.current_step,
            "action_counts": self.action_counts,
            "total_actions": self.total_actions,
            "action_distribution": action_distribution,
            "temperature_start": self.temperature_start,
            "temperature_end": self.temperature_end,
            "temperature_decay": self.temperature_decay,
            "decay_type": self.decay_type,
        }


class AdaptiveExploration:
    """
    Adaptive exploration strategy that combines multiple methods.

    Features:
    - Dynamic strategy selection
    - Performance-based adaptation
    - Multi-armed bandit approach
    - Exploration bonus calculation
    """

    def __init__(
        self,
        strategies: List[Any],
        adaptation_rate: float = 0.1,
        performance_window: int = 1000,
        exploration_bonus: float = 0.1,
    ):
        """
        Initialize adaptive exploration.

        Args:
            strategies: List of exploration strategies
            adaptation_rate: Rate of adaptation
            performance_window: Window for performance evaluation
            exploration_bonus: Bonus for exploration
        """
        self.strategies = strategies
        self.adaptation_rate = adaptation_rate
        self.performance_window = performance_window
        self.exploration_bonus = exploration_bonus

        # State tracking
        self.current_strategy = 0
        self.strategy_performances = [0.0] * len(strategies)
        self.strategy_counts = [0] * len(strategies)
        self.performance_history = []

        # Statistics
        self.total_actions = 0
        self.strategy_switches = 0

        logger.info(
            f"AdaptiveExploration initialized: {len(strategies)} strategies, "
            f"adaptation_rate={adaptation_rate}, performance_window={performance_window}"
        )

    def select_action(
        self, q_values: np.ndarray, step: Optional[int] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Select action using adaptive strategy.

        Args:
            q_values: Q-values for each action
            step: Current step

        Returns:
            Tuple of (selected_action, strategy_info)
        """
        # Select strategy
        strategy = self.strategies[self.current_strategy]

        # Get action from strategy
        if hasattr(strategy, "select_action"):
            result = strategy.select_action(q_values, step)
            if isinstance(result, tuple) and len(result) == 2:
                action, info = result
            else:
                action = result
                info = {}
        else:
            # Fallback to random selection
            action = np.random.randint(len(q_values))
            info = {}

        # Track strategy usage
        self.strategy_counts[self.current_strategy] += 1
        self.total_actions += 1

        # Prepare strategy info
        strategy_info = {
            "strategy_index": self.current_strategy,
            "strategy_type": type(strategy).__name__,
            "strategy_info": info,
            "strategy_performances": self.strategy_performances.copy(),
            "strategy_counts": self.strategy_counts.copy(),
        }

        return action, strategy_info

    def update_performance(self, reward: float, step: Optional[int] = None) -> None:
        """
        Update performance for current strategy.

        Args:
            reward: Reward received
            step: Current step
        """
        # Update performance history
        self.performance_history.append(reward)

        # Keep only recent history
        if len(self.performance_history) > self.performance_window:
            self.performance_history = self.performance_history[
                -self.performance_window :
            ]

        # Update strategy performance
        if len(self.performance_history) >= 10:
            recent_performance = np.mean(self.performance_history[-10:])
            self.strategy_performances[self.current_strategy] = (
                1 - self.adaptation_rate
            ) * self.strategy_performances[
                self.current_strategy
            ] + self.adaptation_rate * recent_performance

        # Check if should switch strategy
        if self._should_switch_strategy():
            self._switch_strategy()

    def _should_switch_strategy(self) -> bool:
        """Check if should switch strategy."""
        if len(self.strategies) <= 1:
            return False

        # Switch if current strategy is underperforming
        current_performance = self.strategy_performances[self.current_strategy]
        best_performance = max(self.strategy_performances)

        # Switch if performance gap is significant
        performance_gap = best_performance - current_performance
        return performance_gap > 0.1  # Threshold for switching

    def _switch_strategy(self) -> None:
        """Switch to best performing strategy."""
        best_strategy = np.argmax(self.strategy_performances)

        if best_strategy != self.current_strategy:
            self.current_strategy = best_strategy
            self.strategy_switches += 1

            logger.info(
                f"Switched to strategy {best_strategy} (performance: {self.strategy_performances[best_strategy]:.4f})"
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get adaptive exploration statistics."""
        return {
            "current_strategy": self.current_strategy,
            "strategy_performances": self.strategy_performances,
            "strategy_counts": self.strategy_counts,
            "strategy_switches": self.strategy_switches,
            "total_actions": self.total_actions,
            "performance_history_length": len(self.performance_history),
            "adaptation_rate": self.adaptation_rate,
            "performance_window": self.performance_window,
        }


def create_exploration_strategy(strategy_type: str, **kwargs) -> Any:
    """
    Factory function to create exploration strategy.

    Args:
        strategy_type: Type of exploration strategy
        **kwargs: Strategy-specific parameters

    Returns:
        Configured exploration strategy
    """
    if strategy_type == "epsilon_greedy":
        return EpsilonGreedyExploration(**kwargs)
    elif strategy_type == "temperature_softmax":
        return TemperatureSoftmaxExploration(**kwargs)
    elif strategy_type == "adaptive":
        # Create multiple strategies for adaptation
        strategies = [
            EpsilonGreedyExploration(**kwargs),
            TemperatureSoftmaxExploration(**kwargs),
        ]
        return AdaptiveExploration(strategies, **kwargs)
    else:
        raise ValueError(f"Unknown exploration strategy: {strategy_type}")


def create_exploration_schedule(
    total_steps: int,
    exploration_ratio: float = 0.1,
    strategy_type: str = "epsilon_greedy",
    **kwargs,
) -> Any:
    """
    Create exploration schedule for training.

    Args:
        total_steps: Total number of training steps
        exploration_ratio: Ratio of steps for exploration
        strategy_type: Type of exploration strategy
        **kwargs: Strategy-specific parameters

    Returns:
        Configured exploration strategy
    """
    exploration_steps = int(total_steps * exploration_ratio)

    # Set default parameters based on strategy type
    if strategy_type == "epsilon_greedy":
        default_params = {
            "epsilon_start": 0.3,
            "epsilon_end": 0.01,
            "epsilon_decay": exploration_steps,
            "decay_type": "linear",
        }
    elif strategy_type == "temperature_softmax":
        default_params = {
            "temperature_start": 1.0,
            "temperature_end": 0.1,
            "temperature_decay": exploration_steps,
            "decay_type": "linear",
        }
    else:
        default_params = {}

    # Update with provided parameters
    default_params.update(kwargs)

    return create_exploration_strategy(strategy_type, **default_params)
