"""
Hyprland anime rice style renderer with pastel colors and kawaii aesthetic.
"""
import pygame
import numpy as np
from .base import BaseRenderer


class HyprlandAnimeRenderer(BaseRenderer):
    """Hyprland anime rice style renderer with pastel colors and kawaii aesthetic."""
    
    def __init__(self, env, window_size):
        super().__init__(env, window_size)
        # Catppuccin-inspired pastel palette
        self.colors = {
            'bg': (30, 30, 46),              # Dark base
            'surface': (49, 50, 68),         # Surface
            'overlay': (69, 71, 90),         # Overlay
            'text': (205, 214, 244),         # Text
            'subtext': (166, 173, 200),      # Subtext
            'lavender': (180, 190, 254),     # Lavender
            'pink': (245, 194, 231),         # Pink
            'mauve': (203, 166, 247),        # Mauve
            'red': (243, 139, 168),          # Red
            'peach': (250, 179, 135),        # Peach
            'yellow': (249, 226, 175),       # Yellow
            'green': (166, 227, 161),        # Green
            'teal': (148, 226, 213),         # Teal
            'sky': (137, 220, 235),          # Sky
            'sapphire': (116, 199, 236),     # Sapphire
            'blue': (137, 180, 250),         # Blue
            'rosewater': (245, 224, 220)     # Rosewater
        }
        self.glow_offset = 0
        self.particle_offset = 0
        
    def _setup_fonts(self):
        """Setup soft rounded fonts."""
        # Try to use soft/rounded fonts
        font_options = ['Segoe UI', 'Arial Rounded MT Bold', 'Helvetica', 'Arial']
        for font_name in font_options:
            try:
                self.title_font = pygame.font.SysFont(font_name, 26, bold=True)
                self.stat_font = pygame.font.SysFont(font_name, 18, bold=True)
                self.proc_font = pygame.font.SysFont(font_name, 15)
                self.small_font = pygame.font.SysFont(font_name, 13)
                return
            except:
                continue
        
        # Fallback
        self.title_font = pygame.font.Font(None, 28)
        self.stat_font = pygame.font.Font(None, 20)
        self.proc_font = pygame.font.Font(None, 17)
        self.small_font = pygame.font.Font(None, 15)
        
    def initialize(self):
        super().initialize()
        pygame.display.set_caption("ramuwu ~ system monitor")
        
    def render(self):
        self.screen.fill(self.colors['bg'])
        
        self.glow_offset = (self.glow_offset + 0.05) % (2 * np.pi)
        self.particle_offset = (self.particle_offset + 0.02) % (2 * np.pi)
        
        # Draw animated background elements
        self._draw_bg_particles()
        
        # Main UI
        self._draw_kawaii_header()
        self._draw_system_cards()
        self._draw_process_cards()
        
        pygame.display.flip()
        self.clock.tick(5)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                
    def _draw_bg_particles(self):
        """Draw floating particles in background."""
        for i in range(15):
            angle = self.particle_offset + i * (2 * np.pi / 15)
            x = int(self.window_size[0] * 0.5 + 300 * np.cos(angle))
            y = int(self.window_size[1] * 0.3 + 150 * np.sin(angle * 1.5))
            
            # Soft glow circles
            color = self.colors['lavender'] if i % 3 == 0 else (
                self.colors['pink'] if i % 3 == 1 else self.colors['sky']
            )
            alpha_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surf, (*color, 30), (10, 10), 10)
            self.screen.blit(alpha_surf, (x - 10, y - 10))
            
    def _draw_kawaii_header(self):
        """Draw cute header with anime aesthetic."""
        # Title with gradient effect
        title_text = "system monitor uwu"
        title_surf = self.title_font.render(title_text, True, self.colors['pink'])
        
        # Shadow effect
        shadow_surf = self.title_font.render(title_text, True, self.colors['overlay'])
        self.screen.blit(shadow_surf, (22, 22))
        self.screen.blit(title_surf, (20, 20))
        
        # Cute symbols (ASCII-safe)
        symbols = ["~", "*", "+", "uwu", "owo"]
        symbol_idx = (self.env.current_step // 10) % len(symbols)
        symbol_surf = self.stat_font.render(symbols[symbol_idx], True, self.colors['mauve'])
        self.screen.blit(symbol_surf, (250, 23))
        
        # Step counter in cute format
        step_text = f"step: {self.env.current_step} nya"
        step_surf = self.small_font.render(step_text, True, self.colors['subtext'])
        self.screen.blit(step_surf, (self.window_size[0] - 160, 25))
        
    def _draw_rounded_rect(self, x, y, width, height, color, radius=15, alpha=255):
        """Draw rounded rectangle with optional transparency."""
        if alpha < 255:
            surf = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(surf, (*color, alpha), (0, 0, width, height), border_radius=radius)
            self.screen.blit(surf, (x, y))
        else:
            pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=radius)
            
    def _draw_glow_rect(self, x, y, width, height, glow_color, radius=15):
        """Draw glowing border around rounded rectangle."""
        glow_intensity = int(50 + 30 * np.sin(self.glow_offset))
        for offset in range(3, 0, -1):
            alpha = glow_intensity // offset
            glow_surf = pygame.Surface((width + offset*2, height + offset*2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*glow_color, alpha), 
                           (0, 0, width + offset*2, height + offset*2), 
                           border_radius=radius + offset, width=2)
            self.screen.blit(glow_surf, (x - offset, y - offset))
            
    def _draw_system_cards(self):
        """Draw system metrics as cute cards."""
        start_y = 65
        card_width = (self.window_size[0] - 60) // 3
        card_height = 110
        
        stats = self.env.system_stats
        metrics = [
            ("RAM <3", stats[0], self.colors['pink'], "ram-chan"),
            ("CPU :)", stats[1], self.colors['blue'], "cpu-kun"),
            ("POWER *", stats[4], self.colors['yellow'], "power-san")
        ]
        
        for i, (label, value, color, nickname) in enumerate(metrics):
            x = 20 + i * (card_width + 10)
            y = start_y
            
            # Card background with transparency
            self._draw_rounded_rect(x, y, card_width, card_height, self.colors['surface'], 12)
            
            # Glow effect for high values
            if value > 0.7:
                self._draw_glow_rect(x, y, card_width, card_height, self.colors['red'], 12)
            
            # Label
            label_surf = self.stat_font.render(label, True, color)
            self.screen.blit(label_surf, (x + 15, y + 12))
            
            # Nickname
            nick_surf = self.small_font.render(nickname, True, self.colors['subtext'])
            self.screen.blit(nick_surf, (x + 15, y + 35))
            
            # Cute percentage display
            percentage = f"{value*100:.1f}%"
            perc_surf = self.title_font.render(percentage, True, self.colors['text'])
            self.screen.blit(perc_surf, (x + 15, y + 55))
            
            # Animated bar
            bar_y = y + card_height - 20
            bar_width = card_width - 30
            
            # Background bar
            self._draw_rounded_rect(x + 15, bar_y, bar_width, 10, self.colors['overlay'], 5)
            
            # Filled bar with gradient effect
            fill_width = int(bar_width * value)
            if fill_width > 0:
                self._draw_rounded_rect(x + 15, bar_y, fill_width, 10, color, 5)
                
                # Glow on bar
                glow_surf = pygame.Surface((fill_width, 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*color, 100), (0, 0, fill_width, 10), border_radius=5)
                self.screen.blit(glow_surf, (x + 15, bar_y - 2))
                
    def _draw_process_cards(self):
        """Draw processes as cute cards."""
        start_y = 195
        card_height = 85
        card_margin = 12
        
        # Section label
        section_surf = self.stat_font.render("processes owo", True, self.colors['lavender'])
        self.screen.blit(section_surf, (20, start_y))
        
        start_y += 35
        
        for i in range(self.env.k):
            ram, cpu, prio, state = self.env.process_table[i]
            y = start_y + i * (card_height + card_margin)
            
            # Card background
            self._draw_rounded_rect(20, y, self.window_size[0] - 40, card_height, 
                                   self.colors['surface'], 10)
            
            # State-based left accent
            state_color = self._get_anime_state_color(state)
            pygame.draw.rect(self.screen, state_color, (20, y, 5, card_height), 
                           border_top_left_radius=10, border_bottom_left_radius=10)
            
            # Process ID with cute format
            pid_text = f"process.{i:02d}"
            pid_surf = self.proc_font.render(pid_text, True, self.colors['text'])
            self.screen.blit(pid_surf, (35, y + 12))
            
            # State badge
            state_text = self._get_anime_state_text(state)
            badge_width = 90
            badge_x = 35
            badge_y = y + 38
            
            self._draw_rounded_rect(badge_x, badge_y, badge_width, 24, 
                                   self.colors['overlay'], 8)
            
            state_surf = self.small_font.render(state_text, True, state_color)
            text_rect = state_surf.get_rect(center=(badge_x + badge_width // 2, badge_y + 12))
            self.screen.blit(state_surf, text_rect)
            
            # Resource bars (only if active)
            if abs(state - 1.0) < 0.01 or abs(state - 0.6) < 0.01:
                bars_x = 150
                
                # RAM bar
                ram_label = self.small_font.render("ram", True, self.colors['subtext'])
                self.screen.blit(ram_label, (bars_x, y + 15))
                
                bar_width = 120
                self._draw_rounded_rect(bars_x + 35, y + 17, bar_width, 8, 
                                       self.colors['overlay'], 4)
                if ram > 0:
                    self._draw_rounded_rect(bars_x + 35, y + 17, int(bar_width * ram), 8, 
                                           self.colors['pink'], 4)
                
                ram_val = self.small_font.render(f"{ram*100:.0f}%", True, self.colors['text'])
                self.screen.blit(ram_val, (bars_x + bar_width + 42, y + 13))
                
                # CPU bar
                cpu_label = self.small_font.render("cpu", True, self.colors['subtext'])
                self.screen.blit(cpu_label, (bars_x, y + 42))
                
                self._draw_rounded_rect(bars_x + 35, y + 44, bar_width, 8, 
                                       self.colors['overlay'], 4)
                if cpu > 0:
                    self._draw_rounded_rect(bars_x + 35, y + 44, int(bar_width * cpu), 8, 
                                           self.colors['blue'], 4)
                
                cpu_val = self.small_font.render(f"{cpu*100:.0f}%", True, self.colors['text'])
                self.screen.blit(cpu_val, (bars_x + bar_width + 42, y + 40))
                
            # Priority indicator
            prio_x = self.window_size[0] - 130
            prio_label = self.small_font.render("priority", True, self.colors['subtext'])
            self.screen.blit(prio_label, (prio_x, y + 20))
            
            prio_val = self.proc_font.render(f"{prio:.2f}", True, self.colors['teal'])
            self.screen.blit(prio_val, (prio_x + 15, y + 38))
            
    def _get_anime_state_color(self, state):
        """Get cute color for process state."""
        if abs(state - 1.0) < 0.01:
            return self.colors['green']
        elif abs(state - 0.6) < 0.01:
            return self.colors['yellow']
        elif abs(state - 0.3) < 0.01:
            return self.colors['mauve']
        else:
            return self.colors['red']
            
    def _get_anime_state_text(self, state):
        """Get cute text for process state."""
        if abs(state - 1.0) < 0.01:
            return "running owo"
        elif abs(state - 0.6) < 0.01:
            return "sleepy zzz"
        elif abs(state - 0.3) < 0.01:
            return "swapped out"
        else:
            return "killed x_x"
