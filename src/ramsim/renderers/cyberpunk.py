"""
Cyberpunk/Neon themed renderer with glowing effects and scanlines.
"""
import pygame
import numpy as np
from .base import BaseRenderer


class CyberpunkRenderer(BaseRenderer):
    """Cyberpunk/Neon themed renderer with glowing effects."""
    
    def __init__(self, env, window_size):
        super().__init__(env, window_size)
        self.colors = {
            'bg': (10, 5, 25),
            'panel_bg': (20, 10, 40),
            'text': (0, 255, 255),
            'text_secondary': (255, 0, 255),
            'ram': (0, 255, 255),
            'cpu': (255, 0, 255),
            'danger': (255, 0, 85),
            'running': (0, 255, 150),
            'suspended': (255, 200, 0),
            'swapped': (120, 0, 255),
            'killed': (60, 60, 80),
            'grid': (100, 0, 150),
            'glow_cyan': (0, 200, 255),
            'glow_magenta': (255, 50, 255)
        }
        self.glitch_offset = 0
        
    def _setup_fonts(self):
        self.title_font = pygame.font.SysFont("Courier New", 28, bold=True)
        self.stat_font = pygame.font.SysFont("Courier New", 18, bold=True)
        self.proc_font = pygame.font.SysFont("Courier New", 14)
        
    def initialize(self):
        super().initialize()
        pygame.display.set_caption(">> CYBERPUNK RAM MONITOR 2077 <<")
        
    def render(self):
        # Background with grid
        self.screen.fill(self.colors['bg'])
        self._draw_grid()
        
        # Top panel
        self._draw_system_panel()
        
        # Process visualization
        self._draw_processes()
        
        # Update display
        pygame.display.flip()
        self.clock.tick(5)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                
    def _draw_grid(self):
        """Draw cyberpunk grid background."""
        grid_color = self.colors['grid']
        for x in range(0, self.window_size[0], 40):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.window_size[1]), 1)
        for y in range(0, self.window_size[1], 40):
            grid_fade = (grid_color[0]//2, grid_color[1]//2, grid_color[2]//2)
            pygame.draw.line(self.screen, grid_fade, (0, y), (self.window_size[0], y), 1)
            
    def _draw_system_panel(self):
        """Draw top system metrics panel."""
        sys_panel_rect = pygame.Rect(20, 20, self.window_size[0] - 40, 100)
        pygame.draw.rect(self.screen, self.colors['panel_bg'], sys_panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.colors['glow_cyan'], sys_panel_rect, 2, border_radius=10)
        pygame.draw.rect(self.screen, (*self.colors['glow_cyan'][:3],), sys_panel_rect.inflate(4, 4), 1, border_radius=11)
        
        # Title with glitch effect
        self.glitch_offset = np.random.randint(-1, 2) if np.random.rand() < 0.1 else 0
        title_text = f">> NEURAL SYSTEM MONITOR << | CYCLE: {self.env.current_step:04d}"
        title_surf = self.title_font.render(title_text, True, self.colors['text'])
        self.screen.blit(title_surf, (sys_panel_rect.x + 15 + self.glitch_offset, sys_panel_rect.y + 12))
        
        # Metrics
        stats = self.env.system_stats
        metrics = [
            (">> RAM", stats[0], self.colors['ram'] if stats[0] < 0.9 else self.colors['danger']),
            (">> CPU", stats[1], self.colors['cpu']),
            (">> PWR", stats[4], self.colors['text_secondary'])
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            x_pos = sys_panel_rect.x + 20 + (i * 250)
            y_pos = sys_panel_rect.y + 55
            
            label_surf = self.stat_font.render(f"{label} [{value*100:05.1f}%]", True, color)
            self.screen.blit(label_surf, (x_pos, y_pos))
            
            # Progress bar
            bar_bg_rect = pygame.Rect(x_pos, y_pos + 25, 220, 12)
            pygame.draw.rect(self.screen, (15, 5, 30), bar_bg_rect)
            pygame.draw.rect(self.screen, color, bar_bg_rect, 1)
            
            fill_width = int(220 * value)
            if fill_width > 0:
                bar_fill_rect = pygame.Rect(x_pos + 2, y_pos + 27, fill_width - 4, 8)
                pygame.draw.rect(self.screen, color, bar_fill_rect)
                if value > 0.8:
                    pygame.draw.rect(self.screen, color, bar_fill_rect.inflate(2, 2), 1)
                    
    def _draw_processes(self):
        """Draw process visualization slots."""
        proc_start_y = 150
        slot_width = (self.window_size[0] - 60) // self.env.k
        slot_height = 400
        bar_max_height = 200
        
        for i in range(self.env.k):
            ram, cpu, prio, state = self.env.process_table[i]
            slot_x = 30 + (i * slot_width)
            
            # Determine state color and text
            state_color, state_text = self._get_state_visuals(state)
            
            # Draw slot
            slot_rect = pygame.Rect(slot_x, proc_start_y, slot_width - 10, slot_height)
            pygame.draw.rect(self.screen, self.colors['panel_bg'], slot_rect, border_radius=8)
            pygame.draw.rect(self.screen, state_color, slot_rect, 2, border_radius=8)
            if abs(state) > 0.01:
                pygame.draw.rect(self.screen, state_color, slot_rect.inflate(2, 2), 1, border_radius=9)
                
            # PID
            pid_surf = self.stat_font.render(f">> P:{i:02X}", True, self.colors['text'])
            self.screen.blit(pid_surf, (slot_x + 10, proc_start_y + 10))
            
            # Draw based on state
            self._draw_process_content(slot_x, proc_start_y, slot_width, bar_max_height, ram, cpu, prio, state)
            
            # State badge
            self._draw_state_badge(slot_x, proc_start_y, slot_width, state_color, state_text, state)
            
    def _get_state_visuals(self, state):
        """Get color and text for a state."""
        if abs(state - 1.0) < 0.01:
            return self.colors['running'], "[ACTIVE]"
        elif abs(state - 0.6) < 0.01:
            return self.colors['suspended'], "[SLEEP]"
        elif abs(state - 0.3) < 0.01:
            return self.colors['swapped'], "[DISK]"
        else:
            return self.colors['killed'], "[TERMINATED]"
            
    def _draw_process_content(self, slot_x, proc_start_y, slot_width, bar_max_height, ram, cpu, prio, state):
        """Draw process bars or special indicators."""
        if abs(state - 1.0) < 0.01:  # ACTIVE
            self._draw_active_bars(slot_x, proc_start_y, bar_max_height, ram, cpu)
        elif abs(state - 0.6) < 0.01:  # SUSPENDED
            self._draw_suspended_visual(slot_x, proc_start_y, bar_max_height, ram)
        elif abs(state - 0.3) < 0.01:  # SWAPPED
            self._draw_swapped_visual(slot_x, proc_start_y, ram)
            
        # Priority indicator
        prio_color = self.colors['danger'] if prio > 0.7 else self.colors['text_secondary']
        prio_surf = self.proc_font.render(f">> PRIO:{prio:.2f}", True, prio_color)
        self.screen.blit(prio_surf, (slot_x + 10, proc_start_y + 295))
        prio_bar = pygame.Rect(slot_x + 10, proc_start_y + 315, int((slot_width - 30) * prio), 4)
        pygame.draw.rect(self.screen, prio_color, prio_bar)
        
    def _draw_active_bars(self, slot_x, proc_start_y, bar_max_height, ram, cpu):
        """Draw neon bars for active processes."""
        # RAM bar
        ram_bar_h = int(ram * bar_max_height)
        ram_bar_rect = pygame.Rect(slot_x + 20, proc_start_y + 50 + (bar_max_height - ram_bar_h), 40, ram_bar_h)
        pygame.draw.rect(self.screen, self.colors['glow_cyan'], ram_bar_rect.inflate(4, 4))
        pygame.draw.rect(self.screen, self.colors['ram'], ram_bar_rect)
        for scan_y in range(0, ram_bar_h, 8):
            pygame.draw.line(self.screen, (0, 200, 200), 
                           (ram_bar_rect.x, ram_bar_rect.y + scan_y),
                           (ram_bar_rect.x + 40, ram_bar_rect.y + scan_y), 1)
        ram_label = self.proc_font.render(f"RAM:{ram:.2f}", True, self.colors['ram'])
        self.screen.blit(ram_label, (slot_x + 15, proc_start_y + 265))
        
        # CPU bar
        cpu_bar_h = int(cpu * bar_max_height)
        cpu_bar_rect = pygame.Rect(slot_x + 80, proc_start_y + 50 + (bar_max_height - cpu_bar_h), 40, cpu_bar_h)
        pygame.draw.rect(self.screen, self.colors['glow_magenta'], cpu_bar_rect.inflate(4, 4))
        pygame.draw.rect(self.screen, self.colors['cpu'], cpu_bar_rect)
        for scan_y in range(0, cpu_bar_h, 8):
            pygame.draw.line(self.screen, (200, 0, 200),
                           (cpu_bar_rect.x, cpu_bar_rect.y + scan_y),
                           (cpu_bar_rect.x + 40, cpu_bar_rect.y + scan_y), 1)
        cpu_label = self.proc_font.render(f"CPU:{cpu:.2f}", True, self.colors['cpu'])
        self.screen.blit(cpu_label, (slot_x + 75, proc_start_y + 265))
        
    def _draw_suspended_visual(self, slot_x, proc_start_y, bar_max_height, ram):
        """Draw dimmed visuals for suspended processes."""
        ram_bar_h = int(ram * bar_max_height)
        ram_bar_rect = pygame.Rect(slot_x + 20, proc_start_y + 50 + (bar_max_height - ram_bar_h), 40, ram_bar_h)
        dim_color = (0, 120, 120)
        pygame.draw.rect(self.screen, dim_color, ram_bar_rect)
        pygame.draw.rect(self.screen, self.colors['suspended'], ram_bar_rect, 1)
        ram_label = self.proc_font.render(f"RAM:{ram:.2f}", True, dim_color)
        self.screen.blit(ram_label, (slot_x + 15, proc_start_y + 265))
        
        cpu_label = self.proc_font.render(f"CPU:0.00", True, (120, 0, 120))
        self.screen.blit(cpu_label, (slot_x + 75, proc_start_y + 265))
        
        sleep_surf = self.proc_font.render("SLEEPING...", True, self.colors['suspended'])
        self.screen.blit(sleep_surf, (slot_x + 15, proc_start_y + 150))
        
    def _draw_swapped_visual(self, slot_x, proc_start_y, ram):
        """Draw disk indicator for swapped processes."""
        disk_rect = pygame.Rect(slot_x + 20, proc_start_y + 80, 100, 150)
        pygame.draw.rect(self.screen, (50, 0, 100), disk_rect, border_radius=5)
        pygame.draw.rect(self.screen, self.colors['swapped'], disk_rect, 2, border_radius=5)
        
        disk_text1 = self.stat_font.render("ON", True, self.colors['swapped'])
        disk_text2 = self.stat_font.render("DISK", True, self.colors['swapped'])
        self.screen.blit(disk_text1, (slot_x + 45, proc_start_y + 120))
        self.screen.blit(disk_text2, (slot_x + 35, proc_start_y + 145))
        
        ram_label = self.proc_font.render(f"RAM:{ram:.2f}", True, (80, 80, 120))
        self.screen.blit(ram_label, (slot_x + 25, proc_start_y + 265))
        
    def _draw_state_badge(self, slot_x, proc_start_y, slot_width, state_color, state_text, state):
        """Draw state badge with pulsing effects."""
        state_bg_rect = pygame.Rect(slot_x + 5, proc_start_y + 340, slot_width - 20, 40)
        pygame.draw.rect(self.screen, (5, 5, 15), state_bg_rect, border_radius=5)
        pygame.draw.rect(self.screen, state_color, state_bg_rect, 3, border_radius=5)
        
        pulse = (np.sin(self.env.current_step * 0.2) + 1) / 2
        if abs(state - 1.0) < 0.01:
            pygame.draw.rect(self.screen, state_color, state_bg_rect.inflate(2, 2), 1, border_radius=6)
        elif abs(state - 0.6) < 0.01:
            if pulse > 0.5:
                pygame.draw.rect(self.screen, state_color, state_bg_rect.inflate(3, 3), 1, border_radius=6)
        elif abs(state - 0.3) < 0.01:
            if pulse > 0.3:
                pygame.draw.rect(self.screen, state_color, state_bg_rect.inflate(2, 2), 1, border_radius=6)
                
        state_surf = self.stat_font.render(state_text, True, state_color)
        text_rect = state_surf.get_rect(center=state_bg_rect.center)
        self.screen.blit(state_surf, text_rect)
