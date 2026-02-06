"""
Retro terminal renderer with ASCII art dashboard and green terminal aesthetic.
"""
import pygame
from .base import BaseRenderer


class RetroTerminalRenderer(BaseRenderer):
    """Retro terminal renderer with ASCII art dashboard."""
    
    def __init__(self, env, window_size):
        super().__init__(env, window_size)
        self.colors = {
            'bg': (0, 0, 0),                 # Pure black
            'green': (0, 255, 0),            # Classic terminal green
            'green_dim': (0, 180, 0),        # Dimmed green
            'green_bright': (0, 255, 128),   # Bright green
            'amber': (255, 191, 0),          # Alternative amber
            'red': (255, 0, 0),              # Warning red
            'yellow': (255, 255, 0),         # Yellow warning
            'border': (0, 200, 0)            # Border green
        }
        self.blink_counter = 0
        
    def _setup_fonts(self):
        """Setup monospace fonts."""
        monospace_fonts = ['Consolas', 'Courier New', 'Lucida Console', 'Monospace']
        for font_name in monospace_fonts:
            try:
                self.title_font = pygame.font.SysFont(font_name, 20, bold=True)
                self.stat_font = pygame.font.SysFont(font_name, 16, bold=True)
                self.proc_font = pygame.font.SysFont(font_name, 14)
                return
            except:
                continue
        
        # Fallback
        self.title_font = pygame.font.Font(None, 22)
        self.stat_font = pygame.font.Font(None, 18)
        self.proc_font = pygame.font.Font(None, 16)
        
    def initialize(self):
        super().initialize()
        pygame.display.set_caption("RAMSIM - TERMINAL v1.0")
        
    def render(self):
        self.screen.fill(self.colors['bg'])
        self.blink_counter = (self.blink_counter + 1) % 60
        
        # Draw terminal interface
        self._draw_header()
        self._draw_system_metrics()
        self._draw_process_table()
        self._draw_footer()
        
        pygame.display.flip()
        self.clock.tick(5)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                
    def _draw_header(self):
        """Draw retro terminal header with blinking cursor."""
        cursor = "_" if self.blink_counter < 30 else " "
        title = f"=== RAM MANAGEMENT SYSTEM v1.0 ==={cursor}"
        title_surf = self.title_font.render(title, True, self.colors['green_bright'])
        self.screen.blit(title_surf, (20, 15))
        
        # Step counter
        step_text = f"STEP: {self.env.current_step:05d}"
        step_surf = self.proc_font.render(step_text, True, self.colors['green_dim'])
        self.screen.blit(step_surf, (self.window_size[0] - 150, 20))
        
    def _draw_box(self, x, y, width, height, title=""):
        """Draw ASCII box borders."""
        # Borders
        pygame.draw.line(self.screen, self.colors['border'], (x, y), (x + width, y), 1)
        pygame.draw.line(self.screen, self.colors['border'], (x, y + height), (x + width, y + height), 1)
        pygame.draw.line(self.screen, self.colors['border'], (x, y), (x, y + height), 1)
        pygame.draw.line(self.screen, self.colors['border'], (x + width, y), (x + width, y + height), 1)
        
        if title:
            title_surf = self.stat_font.render(f"[ {title} ]", True, self.colors['green_bright'])
            self.screen.blit(title_surf, (x + 10, y - 12))
            
    def _draw_ascii_bar(self, x, y, value, color, label, width=200):
        """Draw ASCII-style progress bar."""
        # Label
        label_surf = self.proc_font.render(label, True, self.colors['green'])
        self.screen.blit(label_surf, (x, y))
        
        # Bar area
        bar_x = x + 150
        bracket_l = self.proc_font.render("[", True, self.colors['green_dim'])
        bracket_r = self.proc_font.render("]", True, self.colors['green_dim'])
        self.screen.blit(bracket_l, (bar_x - 10, y))
        self.screen.blit(bracket_r, (bar_x + width + 2, y))
        
        # Fill bar with blocks
        num_blocks = 20
        block_width = width // num_blocks
        filled = int(num_blocks * value)
        
        for i in range(num_blocks):
            bx = bar_x + i * block_width
            if i < filled:
                pygame.draw.rect(self.screen, color, (bx, y, block_width - 2, 12))
            else:
                pygame.draw.line(self.screen, self.colors['green_dim'], 
                               (bx, y + 6), (bx + block_width - 2, y + 6), 1)
        
        # Value text
        value_str = f"{value*100:3.0f}%"
        value_surf = self.proc_font.render(value_str, True, self.colors['green'])
        self.screen.blit(value_surf, (bar_x + width + 15, y))
        
    def _draw_system_metrics(self):
        """Draw system metrics box."""
        y_start = 50
        box_height = 155
        self._draw_box(15, y_start, self.window_size[0] - 30, box_height, "SYSTEM METRICS")
        
        y_offset = y_start + 25
        stats = self.env.system_stats
        
        # Color based on thresholds
        metrics = [
            ("RAM.USAGE", stats[0], self.colors['red'] if stats[0] > 0.8 else self.colors['green']),
            ("CPU.USAGE", stats[1], self.colors['yellow'] if stats[1] > 0.7 else self.colors['green']),
            ("PAGE.FAULTS", stats[2], self.colors['yellow']),
            ("SWAP.USAGE", stats[3], self.colors['red'] if stats[3] > 0.5 else self.colors['green']),
            ("POWER.DRAW", stats[4], self.colors['yellow'] if stats[4] > 0.6 else self.colors['green'])
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            self._draw_ascii_bar(30, y_offset + i * 25, value, color, label)
            
    def _draw_process_table(self):
        """Draw process table with ASCII formatting."""
        table_y = 225
        table_height = self.env.k * 30 + 60
        self._draw_box(15, table_y, self.window_size[0] - 30, table_height, "PROCESS TABLE")
        
        # Table header
        table_y += 25
        header = "PID  | RAM       | CPU       | PRIO  | STATE"
        header_surf = self.proc_font.render(header, True, self.colors['green_bright'])
        self.screen.blit(header_surf, (30, table_y))
        
        # Divider
        divider = "-" * 60
        divider_surf = self.proc_font.render(divider, True, self.colors['green_dim'])
        self.screen.blit(divider_surf, (30, table_y + 18))
        
        # Process rows
        table_y += 35
        for i in range(self.env.k):
            ram, cpu, prio, state = self.env.process_table[i]
            row_y = table_y + i * 30
            
            # Determine state
            if abs(state - 1.0) < 0.01:
                state_text, state_color, state_symbol = "RUN", self.colors['green'], ">"
            elif abs(state - 0.6) < 0.01:
                state_text, state_color, state_symbol = "SLP", self.colors['amber'], "z"
            elif abs(state - 0.3) < 0.01:
                state_text, state_color, state_symbol = "SWP", self.colors['yellow'], "D"
            else:
                state_text, state_color, state_symbol = "X", self.colors['green_dim'], "X"
            
            # Format row data
            pid = f"P{i:02d}"
            ram_bar = "=" * int(10 * ram)
            cpu_bar = "#" * int(10 * cpu)
            
            # Render PID
            pid_surf = self.proc_font.render(pid, True, self.colors['green'])
            self.screen.blit(pid_surf, (30, row_y))
            
            # RAM bar
            ram_text = f"[{ram_bar:<10}]"
            ram_surf = self.proc_font.render(ram_text, True, self.colors['green'])
            self.screen.blit(ram_surf, (100, row_y))
            
            # CPU bar
            cpu_text = f"[{cpu_bar:<10}]"
            cpu_surf = self.proc_font.render(cpu_text, True, self.colors['green'])
            self.screen.blit(cpu_surf, (240, row_y))
            
            # Priority
            prio_text = f"{prio:.2f}"
            prio_surf = self.proc_font.render(prio_text, True, self.colors['green'])
            self.screen.blit(prio_surf, (380, row_y))
            
            # State with symbol
            state_display = f"[{state_symbol}] {state_text}"
            state_surf = self.proc_font.render(state_display, True, state_color)
            self.screen.blit(state_surf, (450, row_y))
            
    def _draw_footer(self):
        """Draw blinking status footer."""
        footer_y = self.window_size[1] - 25
        status = "SYSTEM ONLINE" if self.blink_counter < 30 else "SYSTEM ONLINE "
        footer_surf = self.proc_font.render(f"> {status}", True, self.colors['green_dim'])
        self.screen.blit(footer_surf, (20, footer_y))
