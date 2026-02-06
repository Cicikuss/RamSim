"""
Unit tests for renderer modules.
"""
import pytest
import numpy as np
from ramsim import RamSimEnv


class TestRenderers:
    """Test suite for visualization renderers."""
    
    def test_cyberpunk_renderer_initialization(self):
        """Test CyberpunkRenderer can be initialized."""
        env = RamSimEnv(k=5, render_mode='human', renderer_style='cyberpunk')
        env.reset()
        
        # Trigger renderer initialization
        env.render()
        
        assert env.renderer is not None
        assert env.renderer.screen is not None
        
        env.close()
        
    def test_retro_renderer_initialization(self):
        """Test RetroTerminalRenderer can be initialized."""
        env = RamSimEnv(k=5, render_mode='human', renderer_style='retro')
        env.reset()
        
        env.render()
        
        assert env.renderer is not None
        assert env.renderer.screen is not None
        
        env.close()
        
    def test_anime_renderer_initialization(self):
        """Test HyprlandAnimeRenderer can be initialized."""
        env = RamSimEnv(k=5, render_mode='human', renderer_style='anime')
        env.reset()
        
        env.render()
        
        assert env.renderer is not None
        assert env.renderer.screen is not None
        
        env.close()
        
    def test_no_render_in_headless_mode(self):
        """Test that rendering is skipped in headless mode."""
        env = RamSimEnv(k=5, render_mode=None)
        env.reset()
        
        # This should not initialize renderer
        env.render()
        
        assert env.renderer is None
        env.close()
        
    def test_custom_window_size(self):
        """Test custom window size."""
        custom_size = (1024, 768)
        env = RamSimEnv(k=5, render_mode='human', window_size=custom_size)
        env.reset()
        
        assert env.window_size == custom_size
        
        env.close()
        
    def test_dynamic_window_sizing(self):
        """Test that window size adapts to process count."""
        env_small = RamSimEnv(k=3, render_mode='human', renderer_style='cyberpunk')
        env_large = RamSimEnv(k=20, render_mode='human', renderer_style='cyberpunk')
        
        # Larger process count should result in larger window
        assert env_large.window_size[0] >= env_small.window_size[0]
        
        env_small.close()
        env_large.close()
        
    def test_renderer_colors(self):
        """Test that renderers have proper color definitions."""
        from ramsim.renderers import CyberpunkRenderer, RetroTerminalRenderer, HyprlandAnimeRenderer
        
        env = RamSimEnv(k=5)
        
        # Test Cyberpunk colors
        renderer = CyberpunkRenderer(env, (800, 600))
        assert 'bg' in renderer.colors
        assert 'ram' in renderer.colors
        assert 'cpu' in renderer.colors
        
        # Test Retro colors  
        renderer = RetroTerminalRenderer(env, (800, 600))
        assert 'bg' in renderer.colors
        assert 'green' in renderer.colors
        
        # Test Anime colors
        renderer = HyprlandAnimeRenderer(env, (800, 600))
        assert 'bg' in renderer.colors
        assert 'pink' in renderer.colors
        assert 'lavender' in renderer.colors


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
