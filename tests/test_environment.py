"""
Unit tests for RamSim environment.
"""
import pytest
import numpy as np
from ramsim import RamSimEnv


class TestRamSimEnv:
    """Test suite for RamSimEnv class."""
    
    def test_env_creation(self):
        """Test that environment can be created successfully."""
        env = RamSimEnv(k=5)
        assert env.k == 5
        assert env.render_mode is None
        assert env.renderer_style == 'cyberpunk'
        
    def test_env_with_render_mode(self):
        """Test environment creation with different render modes."""
        env = RamSimEnv(k=3, render_mode='human', renderer_style='retro')
        assert env.render_mode == 'human'
        assert env.renderer_style == 'retro'
        env.close()
        
    def test_reset(self):
        """Test environment reset functionality."""
        env = RamSimEnv(k=5)
        obs, info = env.reset(seed=42)
        
        assert 'system_stats' in obs
        assert 'process_table' in obs
        assert obs['system_stats'].shape == (5,)
        assert obs['process_table'].shape == (5, 4)
        assert info['status'] == 'env_initialized'
        
    def test_action_space(self):
        """Test action space dimensions."""
        env = RamSimEnv(k=10)
        assert env.action_space.nvec.shape == (10,)
        assert all(env.action_space.nvec == 8)
        
    def test_observation_space(self):
        """Test observation space structure."""
        env = RamSimEnv(k=5)
        obs_space = env.observation_space
        
        assert 'system_stats' in obs_space.spaces
        assert 'process_table' in obs_space.spaces
        assert obs_space['system_stats'].shape == (5,)
        assert obs_space['process_table'].shape == (5, 4)
        
    def test_step(self):
        """Test environment step function."""
        env = RamSimEnv(k=5, seed=42)
        obs, _ = env.reset(seed=42)
        
        # Take a random action
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        
        assert isinstance(reward, (int, float))
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert 'step' in info
        assert 'ram_usage' in info
        assert 'cpu_usage' in info
        
    def test_noop_action(self):
        """Test that noop action (action 7) doesn't crash."""
        env = RamSimEnv(k=5)
        env.reset(seed=42)
        
        # All processes do nothing
        action = [7] * 5
        obs, reward, terminated, truncated, info = env.step(action)
        
        assert not terminated  # Should not terminate immediately
        assert isinstance(reward, (int, float))
        
    def test_kill_action(self):
        """Test kill action functionality."""
        env = RamSimEnv(k=5)
        env.reset(seed=42)
        
        # Kill first process
        action = [0] + [7] * 4  # Kill first, noop others
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Check that first process is killed (state = 0)
        assert obs['process_table'][0, 3] == 0.0
        
    def test_swap_out_action(self):
        """Test swap out action."""
        env = RamSimEnv(k=5)
        env.reset(seed=42)
        
        # Swap out first process
        action = [1] + [7] * 4
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Check that first process is swapped (state = 0.3)
        assert obs['process_table'][0, 3] == 0.3
        
    def test_suspend_action(self):
        """Test suspend action."""
        env = RamSimEnv(k=5)
        env.reset(seed=42)
        
        # Suspend first process
        action = [3] + [7] * 4
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Check that first process is suspended (state = 0.6)
        assert obs['process_table'][0, 3] == 0.6
        
    def test_multiple_process_counts(self):
        """Test environment with different process counts."""
        for k in [3, 5, 10, 20]:
            env = RamSimEnv(k=k)
            obs, _ = env.reset()
            assert obs['process_table'].shape == (k, 4)
            
    def test_deterministic_reset(self):
        """Test that reset with same seed produces same initial state."""
        env1 = RamSimEnv(k=5)
        env2 = RamSimEnv(k=5)
        
        obs1, _ = env1.reset(seed=42)
        obs2, _ = env2.reset(seed=42)
        
        np.testing.assert_array_equal(obs1['system_stats'], obs2['system_stats'])
        np.testing.assert_array_equal(obs1['process_table'], obs2['process_table'])
        
    def test_info_metrics(self):
        """Test that info dict contains all required metrics."""
        env = RamSimEnv(k=5)
        env.reset(seed=42)
        action = env.action_space.sample()
        _, _, _, _, info = env.step(action)
        
        required_keys = ['step', 'ram_usage', 'cpu_usage', 'page_faults', 'swap_usage', 'power']
        for key in required_keys:
            assert key in info
            assert isinstance(info[key], (int, float))
            
    def test_system_stats_bounds(self):
        """Test that system stats stay within valid bounds."""
        env = RamSimEnv(k=5)
        env.reset(seed=42)
        
        for _ in range(50):
            action = env.action_space.sample()
            obs, _, terminated, _, _ = env.step(action)
            
            if terminated:
                break
                
            # Check bounds
            assert np.all(obs['system_stats'] >= 0)
            assert np.all(obs['system_stats'] <= 1.1)  # Allow slight overflow for numerical errors
            
    def test_close(self):
        """Test that close method works without errors."""
        env = RamSimEnv(k=5)
        env.reset()
        env.close()
        # Should not raise any exceptions


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
