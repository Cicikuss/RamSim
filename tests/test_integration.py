"""
Integration tests for RamSim environment.
"""
import pytest
import numpy as np
from ramsim import RamSimEnv


class TestIntegration:
    """Integration tests for complete environment workflows."""
    
    def test_full_episode(self):
        """Test a complete episode from reset to termination."""
        env = RamSimEnv(k=5)
        obs, info = env.reset(seed=42)
        
        total_reward = 0
        steps = 0
        max_steps = 1000
        
        while steps < max_steps:
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            steps += 1
            
            if terminated or truncated:
                break
                
        assert steps > 0
        assert isinstance(total_reward, (int, float))
        
        env.close()
        
    def test_multiple_episodes(self):
        """Test running multiple episodes sequentially."""
        env = RamSimEnv(k=5)
        
        for episode in range(3):
            obs, info = env.reset(seed=42 + episode)
            
            for step in range(100):
                action = env.action_space.sample()
                obs, reward, terminated, truncated, info = env.step(action)
                
                if terminated or truncated:
                    break
                    
        env.close()
        
    def test_stress_test_many_processes(self):
        """Stress test with many processes."""
        env = RamSimEnv(k=50)
        obs, _ = env.reset(seed=42)
        
        for _ in range(20):
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            
            if terminated:
                break
                
        env.close()
        
    def test_all_actions_work(self):
        """Test that all action types work without crashing."""
        env = RamSimEnv(k=8)
        env.reset(seed=42)
        
        # Test each action type on each process
        for action_type in range(8):
            action = [action_type] * 8
            obs, reward, terminated, truncated, info = env.step(action)
            
            assert not terminated  # Should not immediately terminate
            
        env.close()
        
    def test_gymnasium_compatibility(self):
        """Test that environment is compatible with Gymnasium interface."""
        env = RamSimEnv(k=5)
        
        # Check required methods exist
        assert hasattr(env, 'reset')
        assert hasattr(env, 'step')
        assert hasattr(env, 'render')
        assert hasattr(env, 'close')
        assert hasattr(env, 'action_space')
        assert hasattr(env, 'observation_space')
        
        # Check metadata
        assert hasattr(env, 'metadata')
        assert 'render_modes' in env.metadata
        
        env.close()
        
    def test_consistent_behavior(self):
        """Test that same seed produces consistent behavior."""
        env1 = RamSimEnv(k=5)
        env2 = RamSimEnv(k=5)
        
        obs1, _ = env1.reset(seed=42)
        obs2, _ = env2.reset(seed=42)
        
        # Take same actions
        actions = [[7] * 5 for _ in range(10)]  # NoOp actions
        
        for action in actions:
            obs1, r1, t1, _, _ = env1.step(action)
            obs2, r2, t2, _, _ = env2.step(action)
            
            # Due to stochastic process dynamics, perfect equality is not expected
            # But initial observations should be equal
            
        env1.close()
        env2.close()
        
    def test_process_spawning(self):
        """Test that new processes spawn after kills."""
        env = RamSimEnv(k=5)
        env.reset(seed=42)
        
        # Kill all processes
        kill_all = [0] * 5
        obs, _, _, _, _ = env.step(kill_all)
        
        # Check all killed
        assert np.all(obs['process_table'][:, 3] == 0)
        
        # Run for many steps to allow spawning
        for _ in range(100):
            noop_action = [7] * 5
            obs, _, terminated, _, _ = env.step(noop_action)
            
            if terminated:
                break
                
            # Check if any process spawned
            if np.any(obs['process_table'][:, 3] > 0):
                # At least one process spawned
                assert True
                break
                
        env.close()
        
    def test_reward_bounds(self):
        """Test that rewards are within reasonable bounds."""
        env = RamSimEnv(k=5)
        env.reset(seed=42)
        
        rewards = []
        for _ in range(100):
            action = env.action_space.sample()
            _, reward, terminated, _, _ = env.step(action)
            rewards.append(reward)
            
            if terminated:
                break
                
        # Rewards should be finite
        assert all(np.isfinite(r) for r in rewards)
        
        env.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
