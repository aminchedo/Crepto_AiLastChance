"""
Unit tests for the PrioritizedExperienceReplayBuffer class
"""

from unittest.mock import Mock, patch

import numpy as np
import pytest

from backend.ml.replay_buffer import PrioritizedExperienceReplayBuffer, SumTree


class TestSumTree:
    """Test cases for SumTree"""

    @pytest.fixture
    def sum_tree(self):
        """Create a SumTree instance for testing."""
        return SumTree(capacity=8)

    def test_sum_tree_initialization(self, sum_tree):
        """Test SumTree initialization."""
        assert sum_tree.capacity == 8
        assert len(sum_tree.tree) == 15  # 2 * capacity - 1
        assert len(sum_tree.data) == 8
        assert sum_tree.data_pointer == 0
        assert sum_tree.n_entries == 0

    def test_sum_tree_add(self, sum_tree):
        """Test adding data to SumTree."""
        data = ("state", "action", "reward", "next_state", "done")
        priority = 1.0

        sum_tree.add(priority, data)

        assert sum_tree.n_entries == 1
        assert sum_tree.data[0] == data
        assert sum_tree.tree[7] == priority  # First leaf node

    def test_sum_tree_add_multiple(self, sum_tree):
        """Test adding multiple items to SumTree."""
        for i in range(5):
            data = (
                f"state_{i}",
                f"action_{i}",
                f"reward_{i}",
                f"next_state_{i}",
                f"done_{i}",
            )
            priority = float(i + 1)
            sum_tree.add(priority, data)

        assert sum_tree.n_entries == 5
        assert sum_tree.data_pointer == 5

        # Check that priorities are stored correctly
        for i in range(5):
            assert sum_tree.data[i] == (
                f"state_{i}",
                f"action_{i}",
                f"reward_{i}",
                f"next_state_{i}",
                f"done_{i}",
            )

    def test_sum_tree_add_capacity_overflow(self, sum_tree):
        """Test SumTree behavior when capacity is exceeded."""
        # Fill capacity
        for i in range(8):
            data = (
                f"state_{i}",
                f"action_{i}",
                f"reward_{i}",
                f"next_state_{i}",
                f"done_{i}",
            )
            sum_tree.add(1.0, data)

        assert sum_tree.n_entries == 8
        assert sum_tree.data_pointer == 0  # Wrapped around

        # Add one more item
        data = ("new_state", "new_action", "new_reward", "new_next_state", "new_done")
        sum_tree.add(2.0, data)

        assert sum_tree.n_entries == 8  # Still 8 entries
        assert sum_tree.data[0] == data  # Overwrote first item
        assert sum_tree.data_pointer == 1

    def test_sum_tree_update(self, sum_tree):
        """Test updating priority in SumTree."""
        # Add item
        data = ("state", "action", "reward", "next_state", "done")
        sum_tree.add(1.0, data)

        # Update priority
        sum_tree.update(7, 2.0)  # Index 7 is the first leaf node

        assert sum_tree.tree[7] == 2.0

    def test_sum_tree_get(self, sum_tree):
        """Test retrieving data from SumTree."""
        # Add items
        for i in range(3):
            data = (
                f"state_{i}",
                f"action_{i}",
                f"reward_{i}",
                f"next_state_{i}",
                f"done_{i}",
            )
            sum_tree.add(float(i + 1), data)

        # Test retrieval
        idx, priority, data = sum_tree.get(1.5)

        assert priority == 2.0  # Should get the second item
        assert data == ("state_1", "action_1", "reward_1", "next_state_1", "done_1")

    def test_sum_tree_total_priority(self, sum_tree):
        """Test total priority calculation."""
        # Add items
        for i in range(3):
            data = (
                f"state_{i}",
                f"action_{i}",
                f"reward_{i}",
                f"next_state_{i}",
                f"done_{i}",
            )
            sum_tree.add(float(i + 1), data)

        total_priority = sum_tree.total_priority()
        expected_total = 1.0 + 2.0 + 3.0  # Sum of priorities

        assert total_priority == expected_total

    def test_sum_tree_propagation(self, sum_tree):
        """Test priority propagation up the tree."""
        # Add items
        for i in range(4):
            data = (
                f"state_{i}",
                f"action_{i}",
                f"reward_{i}",
                f"next_state_{i}",
                f"done_{i}",
            )
            sum_tree.add(float(i + 1), data)

        # Check that root node has correct total
        assert sum_tree.tree[0] == 10.0  # 1 + 2 + 3 + 4

        # Check intermediate nodes
        assert sum_tree.tree[1] == 7.0  # Left subtree: 1 + 2 + 3 + 4
        assert sum_tree.tree[2] == 3.0  # Right subtree: 1 + 2

    def test_sum_tree_edge_cases(self, sum_tree):
        """Test SumTree edge cases."""
        # Test with zero priority
        data = ("state", "action", "reward", "next_state", "done")
        sum_tree.add(0.0, data)

        assert sum_tree.tree[7] == 0.0
        assert sum_tree.total_priority() == 0.0

        # Test with very large priority
        sum_tree.add(1e6, data)

        assert sum_tree.tree[7] == 1e6
        assert sum_tree.total_priority() == 1e6


class TestPrioritizedExperienceReplayBuffer:
    """Test cases for PrioritizedExperienceReplayBuffer"""

    @pytest.fixture
    def replay_buffer(self):
        """Create a PrioritizedExperienceReplayBuffer instance for testing."""
        return PrioritizedExperienceReplayBuffer(capacity=1000)

    @pytest.fixture
    def small_buffer(self):
        """Create a small buffer for testing."""
        return PrioritizedExperienceReplayBuffer(capacity=10)

    def test_buffer_initialization(self, replay_buffer):
        """Test buffer initialization."""
        assert replay_buffer.capacity == 1000
        assert replay_buffer.alpha == 0.6
        assert replay_buffer.beta_start == 0.4
        assert replay_buffer.beta_frames == 100000
        assert replay_buffer.frame == 0
        assert replay_buffer.epsilon == 0.01
        assert replay_buffer.max_priority == 1.0
        assert len(replay_buffer) == 0

    def test_buffer_initialization_custom(self):
        """Test buffer initialization with custom parameters."""
        buffer = PrioritizedExperienceReplayBuffer(
            capacity=500, alpha=0.8, beta_start=0.6, beta_frames=50000
        )

        assert buffer.capacity == 500
        assert buffer.alpha == 0.8
        assert buffer.beta_start == 0.6
        assert buffer.beta_frames == 50000

    def test_store_experience(self, replay_buffer):
        """Test storing experience in buffer."""
        experience = (
            np.array([1, 2, 3]),  # state
            1,  # action
            0.5,  # reward
            np.array([4, 5, 6]),  # next_state
            0,  # done
        )

        replay_buffer.store(experience)

        assert len(replay_buffer) == 1
        assert replay_buffer.max_priority == 1.0

    def test_store_multiple_experiences(self, replay_buffer):
        """Test storing multiple experiences."""
        for i in range(5):
            experience = (
                np.array([i, i + 1, i + 2]),
                i,
                float(i),
                np.array([i + 3, i + 4, i + 5]),
                0,
            )
            replay_buffer.store(experience)

        assert len(replay_buffer) == 5

    def test_sample_experience(self, replay_buffer):
        """Test sampling experience from buffer."""
        # Store some experiences
        for i in range(10):
            experience = (
                np.array([i, i + 1, i + 2]),
                i,
                float(i),
                np.array([i + 3, i + 4, i + 5]),
                0,
            )
            replay_buffer.store(experience)

        # Sample batch
        batch_size = 4
        states, actions, rewards, next_states, dones, idxs, is_weights = (
            replay_buffer.sample(batch_size)
        )

        assert len(states) == batch_size
        assert len(actions) == batch_size
        assert len(rewards) == batch_size
        assert len(next_states) == batch_size
        assert len(dones) == batch_size
        assert len(idxs) == batch_size
        assert len(is_weights) == batch_size

        # Check data types
        assert isinstance(states, np.ndarray)
        assert isinstance(actions, np.ndarray)
        assert isinstance(rewards, np.ndarray)
        assert isinstance(next_states, np.ndarray)
        assert isinstance(dones, np.ndarray)
        assert isinstance(idxs, list)
        assert isinstance(is_weights, np.ndarray)

    def test_sample_empty_buffer(self, replay_buffer):
        """Test sampling from empty buffer."""
        with pytest.raises(ValueError):
            replay_buffer.sample(1)

    def test_sample_larger_than_buffer(self, small_buffer):
        """Test sampling more experiences than buffer contains."""
        # Store 3 experiences
        for i in range(3):
            experience = (
                np.array([i, i + 1, i + 2]),
                i,
                float(i),
                np.array([i + 3, i + 4, i + 5]),
                0,
            )
            small_buffer.store(experience)

        # Try to sample 5 experiences
        batch_size = 5
        states, actions, rewards, next_states, dones, idxs, is_weights = (
            small_buffer.sample(batch_size)
        )

        # Should get 3 experiences (all available)
        assert len(states) == 3
        assert len(actions) == 3
        assert len(rewards) == 3
        assert len(next_states) == 3
        assert len(dones) == 3
        assert len(idxs) == 3
        assert len(is_weights) == 3

    def test_update_priorities(self, replay_buffer):
        """Test updating priorities."""
        # Store experiences
        for i in range(5):
            experience = (
                np.array([i, i + 1, i + 2]),
                i,
                float(i),
                np.array([i + 3, i + 4, i + 5]),
                0,
            )
            replay_buffer.store(experience)

        # Sample to get indices
        states, actions, rewards, next_states, dones, idxs, is_weights = (
            replay_buffer.sample(3)
        )

        # Update priorities
        errors = [0.1, 0.2, 0.3]
        replay_buffer.update_priorities(idxs, errors)

        # Check that max_priority was updated
        assert replay_buffer.max_priority > 1.0

    def test_beta_by_frame(self, replay_buffer):
        """Test beta calculation by frame."""
        # Test initial beta
        beta = replay_buffer.beta_by_frame(0)
        assert beta == replay_buffer.beta_start

        # Test beta at half frames
        beta = replay_buffer.beta_by_frame(replay_buffer.beta_frames // 2)
        expected_beta = replay_buffer.beta_start + (1.0 - replay_buffer.beta_start) / 2
        assert abs(beta - expected_beta) < 1e-6

        # Test beta at max frames
        beta = replay_buffer.beta_by_frame(replay_buffer.beta_frames)
        assert beta == 1.0

        # Test beta beyond max frames
        beta = replay_buffer.beta_by_frame(replay_buffer.beta_frames * 2)
        assert beta == 1.0

    def test_importance_sampling_weights(self, replay_buffer):
        """Test importance sampling weight calculation."""
        # Store experiences with different priorities
        for i in range(5):
            experience = (
                np.array([i, i + 1, i + 2]),
                i,
                float(i),
                np.array([i + 3, i + 4, i + 5]),
                0,
            )
            replay_buffer.store(experience)

        # Sample batch
        states, actions, rewards, next_states, dones, idxs, is_weights = (
            replay_buffer.sample(3)
        )

        # Check that importance sampling weights are normalized
        assert np.all(is_weights >= 0)  # All weights should be non-negative
        assert np.max(is_weights) == 1.0  # Maximum weight should be 1.0

    def test_buffer_capacity_overflow(self, small_buffer):
        """Test buffer behavior when capacity is exceeded."""
        # Fill buffer beyond capacity
        for i in range(15):  # More than capacity (10)
            experience = (
                np.array([i, i + 1, i + 2]),
                i,
                float(i),
                np.array([i + 3, i + 4, i + 5]),
                0,
            )
            small_buffer.store(experience)

        # Should only contain capacity number of experiences
        assert len(small_buffer) == small_buffer.capacity

        # Should contain the most recent experiences
        states, actions, rewards, next_states, dones, idxs, is_weights = (
            small_buffer.sample(10)
        )
        assert len(states) == 10

    def test_buffer_frame_increment(self, replay_buffer):
        """Test that frame counter increments on sampling."""
        # Store experiences
        for i in range(5):
            experience = (
                np.array([i, i + 1, i + 2]),
                i,
                float(i),
                np.array([i + 3, i + 4, i + 5]),
                0,
            )
            replay_buffer.store(experience)

        initial_frame = replay_buffer.frame

        # Sample
        replay_buffer.sample(3)

        assert replay_buffer.frame == initial_frame + 1

    def test_buffer_epsilon_handling(self, replay_buffer):
        """Test epsilon handling in priority calculation."""
        # Store experiences
        for i in range(5):
            experience = (
                np.array([i, i + 1, i + 2]),
                i,
                float(i),
                np.array([i + 3, i + 4, i + 5]),
                0,
            )
            replay_buffer.store(experience)

        # Sample to get indices
        states, actions, rewards, next_states, dones, idxs, is_weights = (
            replay_buffer.sample(3)
        )

        # Update with zero errors (should still have epsilon)
        errors = [0.0, 0.0, 0.0]
        replay_buffer.update_priorities(idxs, errors)

        # Check that priorities include epsilon
        assert replay_buffer.max_priority >= replay_buffer.epsilon

    def test_buffer_performance(self, replay_buffer):
        """Test buffer performance benchmarks."""
        import time

        # Store many experiences
        start_time = time.time()

        for i in range(1000):
            experience = (
                np.random.randn(10),  # state
                np.random.randint(0, 3),  # action
                np.random.randn(),  # reward
                np.random.randn(10),  # next_state
                np.random.randint(0, 2),  # done
            )
            replay_buffer.store(experience)

        store_time = time.time() - start_time

        # Should store 1000 experiences quickly (under 1 second)
        assert store_time < 1.0, f"Storing took {store_time:.3f}s, expected < 1.0s"

        # Test sampling performance
        start_time = time.time()

        for _ in range(100):
            replay_buffer.sample(32)

        sample_time = time.time() - start_time

        # Should sample quickly (under 1 second for 100 batches)
        assert sample_time < 1.0, f"Sampling took {sample_time:.3f}s, expected < 1.0s"

    def test_buffer_memory_usage(self, replay_buffer):
        """Test buffer memory usage."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024

        # Store many experiences
        for i in range(10000):
            experience = (
                np.random.randn(100),  # Large state
                np.random.randint(0, 3),
                np.random.randn(),
                np.random.randn(100),  # Large next_state
                np.random.randint(0, 2),
            )
            replay_buffer.store(experience)

        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (under 100MB)
        assert (
            memory_increase < 100
        ), f"Memory increased by {memory_increase:.1f}MB, expected < 100MB"

    def test_buffer_edge_cases(self, replay_buffer):
        """Test buffer edge cases."""
        # Test with single experience
        experience = (np.array([1, 2, 3]), 1, 0.5, np.array([4, 5, 6]), 0)
        replay_buffer.store(experience)

        # Sample single experience
        states, actions, rewards, next_states, dones, idxs, is_weights = (
            replay_buffer.sample(1)
        )

        assert len(states) == 1
        assert len(actions) == 1
        assert len(rewards) == 1
        assert len(next_states) == 1
        assert len(dones) == 1
        assert len(idxs) == 1
        assert len(is_weights) == 1

        # Test with zero capacity (should raise error)
        with pytest.raises(ValueError):
            PrioritizedExperienceReplayBuffer(capacity=0)

    def test_buffer_data_integrity(self, replay_buffer):
        """Test that buffer maintains data integrity."""
        # Store experiences with known values
        stored_experiences = []
        for i in range(10):
            experience = (
                np.array([i, i + 1, i + 2]),
                i,
                float(i),
                np.array([i + 3, i + 4, i + 5]),
                0,
            )
            replay_buffer.store(experience)
            stored_experiences.append(experience)

        # Sample multiple times and check data integrity
        for _ in range(5):
            states, actions, rewards, next_states, dones, idxs, is_weights = (
                replay_buffer.sample(5)
            )

            # Check that sampled data matches stored data
            for i, (state, action, reward, next_state, done) in enumerate(
                zip(states, actions, rewards, next_states, dones)
            ):
                # Find corresponding stored experience
                found = False
                for stored_exp in stored_experiences:
                    if (
                        np.array_equal(state, stored_exp[0])
                        and action == stored_exp[1]
                        and reward == stored_exp[2]
                        and np.array_equal(next_state, stored_exp[3])
                        and done == stored_exp[4]
                    ):
                        found = True
                        break

                assert found, "Sampled experience not found in stored experiences"

    def test_buffer_concurrent_access(self, replay_buffer):
        """Test buffer with concurrent access."""
        import threading
        import time

        results = []

        def store_experiences():
            for i in range(100):
                experience = (
                    np.array([i, i + 1, i + 2]),
                    i,
                    float(i),
                    np.array([i + 3, i + 4, i + 5]),
                    0,
                )
                replay_buffer.store(experience)
                time.sleep(0.001)

        def sample_experiences():
            for _ in range(50):
                try:
                    states, actions, rewards, next_states, dones, idxs, is_weights = (
                        replay_buffer.sample(4)
                    )
                    results.append(len(states))
                except ValueError:
                    # Buffer might be empty
                    pass
                time.sleep(0.001)

        # Create threads
        store_thread = threading.Thread(target=store_experiences)
        sample_thread = threading.Thread(target=sample_experiences)

        # Start threads
        store_thread.start()
        sample_thread.start()

        # Wait for completion
        store_thread.join()
        sample_thread.join()

        # Check that some sampling occurred
        assert len(results) > 0
