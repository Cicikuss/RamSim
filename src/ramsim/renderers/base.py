"""
Base renderer class for RamSim visualizations.
"""
import pygame
import os


class BaseRenderer:
    """Abstract base class for all renderers."""
    
    def __init__(self, env, window_size):
        """
        Initialize base renderer.
        
        Args:
            env: The RamSim environment instance
            window_size: Tuple of (width, height) for the window
        """
        self.env = env
        self.window_size = window_size
        self.screen = None
        self.clock = None
        self.colors = {}
        
    def initialize(self):
        """Initialize Pygame and create window."""
        if self.screen is None:
            pygame.init()
            pygame.display.init()
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 100)
            self.screen = pygame.display.set_mode(self.window_size)
            self.clock = pygame.time.Clock()
            self._setup_fonts()
            
    def _setup_fonts(self):
        """Setup fonts for this renderer. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _setup_fonts()")
        
    def render(self):
        """Main render loop. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement render()")
        
    def close(self):
        """Cleanup and close window."""
        if self.screen is not None:
            pygame.display.quit()
            pygame.quit()
            self.screen = None
