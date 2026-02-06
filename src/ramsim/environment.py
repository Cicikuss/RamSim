"""
RamSim - RAM Management Simulation Environment for Reinforcement Learning.
"""
import gymnasium as gym
from gymnasium.spaces import MultiDiscrete
import numpy as np

from .utils.constants import (
    RAM_USAGE_INDEX, CPU_USAGE_INDEX, PAGE_FAULTS_INDEX, 
    SWAP_USAGE_INDEX, POWER_INDEX
)


class RamSimEnv(gym.Env):
    """
    RAM Simulator Environment - Manages k processes in the system.
    
    A Gymnasium-based Reinforcement Learning environment that simulates RAM management 
    in an operating system, enabling agents to learn resource management strategies.
    
    Args:
        k (int): Number of processes to monitor in the system (default: 5)
        render_mode (str): Rendering mode - 'human' for visualization, None for headless
        renderer_style (str): Visual theme - 'cyberpunk', 'retro', or 'anime' (default: 'cyberpunk')
        window_size (tuple): Window size (width, height). If None, auto-calculated based on k
    
    Action Space:
        8 possible actions for each process:
        0 - Kill: Terminate the process
        1 - Swap/Page-Out: Move process to swap space
        2 - Swap/Page-In: Bring process back from swap space
        3 - Suspend/Stop: Pause the process
        4 - Resume: Resume a suspended process
        5 - Renice/Increase: Increase process priority
        6 - Renice/Decrease: Decrease process priority
        7 - Noop: Do nothing
        
    Observation Space:
        Dictionary with:
        - system_stats: [RAM usage, CPU usage, Page faults, Swap usage, Power consumption]
        - process_table: k × 4 matrix with [RAM, CPU, Priority, State] for each process
    """
    
    metadata = {"render_modes": ["human"], "render_fps": 5}
    
    def __init__(self, k=5, render_mode=None, renderer_style='cyberpunk', window_size=None):
        """Initialize the RamSim environment."""
        self.k = k
        self.action_space = MultiDiscrete([8]*self.k)
        self.observation_space = gym.spaces.Dict({
            # System state: [RAM usage, CPU usage, Page faults, Swap usage, Power consumption (Watt)]
            "system_stats": gym.spaces.Box(low=0, high=1, shape=(5,), dtype=np.float32),
            # Process table: Each row is a process [RAM, CPU, Priority,State(1=Running,0.6=Suspended,0.3=Swapped, 0=Killed)]
            "process_table": gym.spaces.Box(low=0, high=1, shape=(self.k, 4), dtype=np.float32)
        })

        self.system_stats = np.zeros((5,), dtype=np.float32)
        self.process_table = np.zeros((self.k,4), dtype=np.float32)
        self.current_step = 0
        self.swapped_processes = np.zeros((self.k,4), dtype=np.float32)
        self.handlers = [
            self._handle_kill, 
            self._handle_swap_out, 
            self._handle_swap_in, 
            self._handle_suspend, 
            self._handle_resume, 
            self._handle_renice_increase, 
            self._handle_renice_decrease, 
            self._handle_noop
        ]
        
        self.render_mode = render_mode
        self.renderer_style = renderer_style
        
        # Dynamic window sizing based on process count
        if window_size is None:
            # Calculate optimal width and height based on renderer style
            if renderer_style == 'anime' or renderer_style == 'hyprland':
                optimal_width = max(700, min(1200, 700))
                optimal_height = max(400, 230 + (self.k * 97))  # Cards are 85px + 12px margin
            elif renderer_style == 'retro':
                optimal_width = max(700, min(1200, 700))
                optimal_height = max(400, 340 + (self.k * 30))  # 30px per process row
            else:  # cyberpunk
                optimal_width = max(800, min(1920, (self.k * 160) + 60))
                optimal_height = 650
            self.window_size = (optimal_width, optimal_height)
        else:
            self.window_size = window_size
            
        self.renderer = None

   
    def reset(self, seed=None, options=None):
        """
        Resets the environment to a non-deterministic initial state.
        
        This method initializes the process table with a diverse set of process profiles
        (Heavy, Leaky, Active, Idle) to ensure the agent learns to differentiate between 
        legitimate high-resource usage and anomalous behavior.
        """
        super().reset(seed=seed)
        
        # 1. Internal State Initialization
        self.current_step = 0
        
        # 2. Stochastic Process Distribution
        # Define counts for different process profiles to vary scenario difficulty
        heavy_count = np.random.randint(0, 2)  # High-load tasks
        leaky_count = np.random.randint(0, 2)  # Memory leakage anomalies
        # Allocate remaining slots between active users and idle system background
        active_count = np.random.randint(0, self.k - heavy_count - leaky_count + 1)
        
        # Temporary list to store process vectors: [RAM, CPU, Priority, State]
        processes = []
        
        # --- Profile Generation ---
        # Heavy: Significant CPU load and high memory footprint
        for _ in range(heavy_count):
            processes.append([np.random.uniform(0.4, 0.6), np.random.uniform(0.6, 0.9), 
                              np.random.uniform(0.7, 1.0), 1.0])
        
        # Leaky: Anomalous RAM growth with negligible CPU activity
        for _ in range(leaky_count):
            processes.append([np.random.uniform(0.6, 0.8), np.random.uniform(0.0, 0.05), 
                              np.random.uniform(0.0, 0.2), 1.0])
        
        # Active: Standard operational processes with moderate resource demand
        for _ in range(active_count):
            processes.append([np.random.uniform(0.1, 0.4), np.random.uniform(0.2, 0.5), 
                              np.random.uniform(0.4, 0.7), 1.0])
        
        # Idle: Baseline background tasks with minimal footprint
        while len(processes) < self.k:
            processes.append([np.random.uniform(0.01, 0.05), np.random.uniform(0.0, 0.02), 
                              np.random.uniform(0.1, 0.4), 1.0])

        # Shuffle to ensure spatial invariance (prevents positional bias in the Neural Network)
        np.random.shuffle(processes)
        self.process_table = np.array(processes, dtype=np.float32)
        self.swapped_processes = np.zeros((self.k,4), dtype=np.float32)

        # === 3. Telemetry & System Metrics Computation ===
        
        # Model kernel-space overhead (Baseline RAM consumption)
        base_os_load = 0.10
        
        # Compute aggregate resource utilization
        total_cpu_usage = np.clip(np.sum(self.process_table[:, 1]), 0, 1)
        total_ram_usage = np.sum(self.process_table[:, 0]) + base_os_load
        
        # Model Page Fault Rate using a logistic (sigmoid) function.
        # Page faults increase non-linearly as memory pressure exceeds 80%.
        page_fault = 1 / (1 + np.exp(-(total_ram_usage - 0.8) * 10))
        
        # Determine Swap Space utilization based on memory overflow
        raw_swap = np.max([0, total_ram_usage - 1.0])
        swap_usage = np.clip(raw_swap / 1.0, 0, 1) # Normalized to a theoretical 1GB swap limit
        
        # Estimate Power Consumption (Wattage)
        # Modeled as: $P_{total} = P_{static} + \sum P_{dynamic}(CPU, RAM)$ 
        # Normalized against a theoretical maximum of 200W
        raw_power = 50 + (total_cpu_usage * 100) + (total_ram_usage * 40)
        power = np.clip(raw_power / 200, 0, 1)

        # Consolidate telemetry into the system_stats vector
        self.system_stats = np.array([
            np.clip(total_ram_usage, 0, 1), 
            total_cpu_usage, 
            page_fault, 
            swap_usage, 
            power
        ], dtype=np.float32)
        
        return self._get_obs(), {"status": "env_initialized"}


    def _get_obs(self):
        """Get current observation."""
        return {
            "system_stats": self.system_stats,
            "process_table": self.process_table
        }

    def _handle_kill(self, index):
        """
        Kills the process at the given index and updates the process table.
        
        Args:
            index (int): Index of the process to kill
        """
        if self.process_table[index, 3] != 0:
            ram, cpu, priority, state = self.process_table[index]
            reward = 0
            # Scenario 1: High Priority (System/User Critical)
            if ram > 0.4 and priority > 0.6:
                reward = -10  # Heavy penalty for killing critical tasks
                
            # Scenario 2: Memory Leak (The "Ideal" Target)
            elif ram > 0.4 and priority <= 0.2 and cpu < 0.1:
                reward = 20  # High reward for a perfect kill
                
            # Scenario 3: Normal Processes (Active/Idle)
            else:
                # Killing a healthy process should be a slight penalty 
                # unless the system is in crisis (OOM)
                reward = -2 
            
            # Perform the Kill: Wipe the table and internal swap tracking
            self.process_table[index] = np.array([0, 0, 0, 0], dtype=np.float32)
            self.swapped_processes[index] = np.array([0,0,0,0], dtype=np.float32)
        else:
            reward = -1 # Penalty for trying to kill an already killed process
        return reward

    def _handle_swap_out(self, index):
        """
        Moves a process from RAM to Disk. 
        Memory is freed (set to 0) but the process footprint is backed up.
        """
        ram, cpu, priority, state = self.process_table[index]
        
        # 1. Check for invalid states
        if state == 0.3:  # Already swapped
            return -2     # Penalty for redundancy
        if state == 0:    # Already killed
            return -5     # Penalty for trying to swap a ghost process

        # 2. Determine Reward Base
        # Swapping a suspended process is more 'system-friendly'
        if state == 0.6:
            reward = 5
        else:
            reward = 2  # Base reward for a running process

        # 3. High Memory Pressure Bonus
        # Extra incentive for the agent to clear RAM when system is at risk
        if self.system_stats[RAM_USAGE_INDEX] >= 0.8:
            reward += 10

        # 4. Perform the Swap-Out (Logic Refactored here to avoid repetition)
        # Backup the full process data [RAM, CPU, Priority, State] for future Swap-In
        self.swapped_processes[index] = self.process_table[index].copy()
        
        # Update Process Table:
        # We set RAM and CPU to 0, but KEEP Priority so the agent knows its importance.
        # State is updated to 0.3 (Swapped).
        self.process_table[index] = np.array([0, 0, priority, 0.3], dtype=np.float32)

        return reward
        

    def _handle_swap_in(self, index):
        """
        Brings a swapped-out process back into RAM.
        
        Args:
            index (int): Index of the process to swap in
        """
        ram, cpu, priority, state = self.process_table[index]
        # 1. Check for invalid states
        if state != 0.3:  # Not swapped
            return -2     # Penalty for invalid swap-in
        # 2. Perform the Swap-In
        # Restore the full process data from the backup
        backup = self.swapped_processes[index]
        original_ram, original_cpu, original_priority, _ = backup
        predicted_ram_usage = self.system_stats[RAM_USAGE_INDEX] + original_ram
        if predicted_ram_usage > 1.0:
            return -10  # Penalty for causing OOM
        reward = original_priority * 5  # Reward scaled by priority
        if predicted_ram_usage >= 0.8:
            reward -= 15  # Penalty for bringing back high memory usage under pressure
        self.process_table[index] = np.array([original_ram, original_cpu, original_priority, 1.0], dtype=np.float32)
        self.swapped_processes[index] = np.array([0,0,0,0], dtype=np.float32)  # Clear backup
        return reward


    def _handle_suspend(self, index):
        """
        Suspends the process at the given index and updates the process table.
        
        Args:
            index (int): Index of the process to suspend
        """
        ram, cpu, priority, state = self.process_table[index]
        if state == 0.6:  # Already suspended
            return -2     # Penalty for redundancy
        elif state == 0.3:  # Swapped out
            return -3     # Penalty for trying to suspend a swapped process
        elif state == 0:    # Already killed
            return -5     # Penalty for trying to suspend a ghost process
        # Suspend the process: Update state to 0.6 (Suspended)
        self.process_table[index, 3] = 0.6
        #Suspend the process: Reduce CPU usage to 10% of original
        self.process_table[index, 1] = 0
        #Suspend the process: Reduce RAM usage to 50% of original
        self.process_table[index, 0] *= 0.5

        #Reward for suspending high RAM processes
        reward = 0
        if ram > 0.4:
            reward += 5
        if self.system_stats[RAM_USAGE_INDEX] >= 0.8:
            reward += 10 # Extra reward under high memory pressure
        
        if priority > 0.6:
            reward -= 12 # Penalty for suspending high priority processes
        return reward
        

    def _handle_resume(self, index):
        """
        Resumes a suspended process.
        
        Args:
            index (int): Index of the process to resume
        """
        ram, cpu, priority, state = self.process_table[index]
        if state != 0.6:  # Not suspended
            return -2     # Penalty for invalid resume
        original_ram = ram * 2  # Since we halved RAM on suspend
        # Predict RAM usage after resuming
        predicted_ram_usage = self.system_stats[RAM_USAGE_INDEX] + original_ram  # Since we halved RAM on suspend
        if predicted_ram_usage > 1.0:
            return -10  # Penalty for causing OOM
        # Resume the process: Update state to 1.0 (Running)
        self.process_table[index, 3] = 1.0
        # Resume the process: Restore CPU usage to original (Assuming original CPU is double the current)
        self.process_table[index, 1] = 0.2 #wake up with 20% CPU usage
        # Resume the process: Restore RAM usage to original
        self.process_table[index, 0] = original_ram
        reward = priority * 5  # Reward scaled by priority
        if predicted_ram_usage >= 0.8:
            reward -= 15  # Penalty for resuming high memory usage under pressure
        return reward

    def _handle_renice_decrease(self, index):
        """
        Decreases the priority (renice) of a process.
        
        Args:
            index (int): Index of the process to renice
        """
        ram , cpu , priority, state = self.process_table[index]
        if state == 0:    # Already killed
            return -5     # Penalty for trying to renice a ghost process
        if priority <= 0.1:
            return -2     # Penalty for trying to decrease priority beyond min
        old_priority = priority
        new_priority = np.clip(priority - 0.2, 0.0, 1.0)
        self.process_table[index, 2] = new_priority
        reward = 0
        #Reward for decreasing priority of leaky processes
        if ram >0.6 and cpu < 0.05:
            reward += 10
        #Penalty for decreasing priority of high priority processes
        elif old_priority > 0.6 and cpu > 0.4:
            reward -= 8
        return reward
        
    def _handle_renice_increase(self, index):
        """
        Increases the priority (renice) of a process.
        
        Args:
            index (int): Index of the process to renice
        """
        ram , cpu , priority, state = self.process_table[index]
        if state == 0:    # Already killed
            return -5     # Penalty for trying to renice a ghost process
        if priority >= 0.95:
            return -2     # Penalty for trying to increase priority beyond max
        old_priority = priority
        new_priority = np.clip(priority + 0.2, 0.0, 1.0)
        self.process_table[index, 2] = new_priority
        reward = 0
        #Reward for increasing priority of high CPU processes
        if cpu >0.5:
            reward += 10
        #Penalty for increasing priority of low priority processes
        elif old_priority < 0.2 and ram < 0.1:
            reward -= 8
        return reward

    def _handle_noop(self, index):
        """
        No operation for the process at the given index.
        
        Args:
            index (int): Index of the process to perform noop
        """
        return 0  # No reward or penalty for noop
        
    def _update_system_stats(self):
        """Recalculates the system statistics based on the current process table."""
        base_os_load = 0.10
        total_cpu_usage = np.clip(np.sum(self.process_table[:, 1]), 0, 1)
        total_ram_usage = np.sum(self.process_table[:, 0]) + base_os_load
        page_fault = 1 / (1 + np.exp(-(total_ram_usage - 0.8) * 10))
        raw_swap = np.max([0, total_ram_usage - 1.0])
        swap_usage = np.clip(raw_swap / 1.0, 0, 1)
        raw_power = 50 + (total_cpu_usage * 100) + (total_ram_usage * 40)
        power = np.clip(raw_power / 200, 0, 1)

        self.system_stats = np.array([
            np.clip(total_ram_usage, 0, 1), 
            total_cpu_usage, 
            page_fault, 
            swap_usage, 
            power
        ], dtype=np.float32)
    
    def _calculate_global_reward(self):
        """Calculate global reward based on system stability and QoS metrics."""
        total_ram_usage , total_cpu_usage , page_faults , swap_usage , power = self.system_stats
        reward = 0
        # Crash Risk Penalty
        r_stability = -10 if total_ram_usage >= 0.9 else 1.0
        r_power = (1 - power) * 2  # Reward for lower power consumption
        r_qos  = np.sum(self.process_table[:,2] * (self.process_table[:,-1] == 1.0))  # Reward for keeping high priority processes running
        r_trashing = -(swap_usage + page_faults) * 5  # Penalty for swap and page faults
        reward = (0.4 * r_stability) + (0.2 * r_power) + (0.3 * r_qos) + (0.1 * r_trashing)
        return reward
    
    def _apply_process_dynamics(self):
        """
        Simulates the natural dynamics of processes over time, such as memory growth for leaky processes
        and CPU usage fluctuations for active processes. This method should be called at the end of each step
        to update the process table based on their profiles and current state.
        """
        for i in range(self.k):
            ram, cpu, priority, state = self.process_table[i]
            if state == 1.0:  # Running
                cpu_jitter = np.random.uniform(-0.05, 0.05)  # Simulate CPU usage fluctuations
                self.process_table[i, 1] = np.clip(cpu + cpu_jitter, 0.01, 0.95)
                if ram > 0.6 and cpu < 0.1:  # Leaky process
                    leak_amount = np.random.uniform(0.01, 0.06)  # Simulate memory leak growth
                    self.process_table[i, 0] = np.clip(ram + leak_amount, 0, 1)
                else:
                    ram_jitter = np.random.uniform(-0.02, 0.02)  # Simulate RAM usage fluctuations
                    self.process_table[i, 0] = np.clip(ram + ram_jitter, 0.01, 0.95)
                
                # Randomly terminate processes (2% chance per step)
                if np.random.rand() < 0.02:
                    self.process_table[i] = np.array([0, 0, 0, 0], dtype=np.float32)
                    
    def _spawn_new_process(self):
        """
        Spawns a new process to replace killed/terminated processes.
        This maintains system realism where new processes continuously appear.
        """
        # Find killed processes (state == 0)
        killed_indices = np.where(self.process_table[:, 3] == 0)[0]
        
        for idx in killed_indices:
            # 5% chance to spawn a new process per killed slot per step
            if np.random.rand() < 0.05:
                profile_type = np.random.choice(['idle', 'active', 'heavy', 'leaky'], 
                                              p=[0.5, 0.3, 0.15, 0.05])
                
                if profile_type == 'heavy':
                    self.process_table[idx] = [np.random.uniform(0.4, 0.6), 
                                              np.random.uniform(0.6, 0.9), 
                                              np.random.uniform(0.7, 1.0), 1.0]
                elif profile_type == 'leaky':
                    self.process_table[idx] = [np.random.uniform(0.3, 0.5), 
                                              np.random.uniform(0.0, 0.05), 
                                              np.random.uniform(0.0, 0.2), 1.0]
                elif profile_type == 'active':
                    self.process_table[idx] = [np.random.uniform(0.1, 0.4), 
                                              np.random.uniform(0.2, 0.5), 
                                              np.random.uniform(0.4, 0.7), 1.0]
                else:  # idle
                    self.process_table[idx] = [np.random.uniform(0.01, 0.05), 
                                              np.random.uniform(0.0, 0.02), 
                                              np.random.uniform(0.1, 0.4), 1.0]


    def step(self, action):
        """
        Executes the given action on the processes and updates the environment state.
        
        Args:
            action (list): List of actions for each process (length k)
            
        Returns:
            observation (dict): Updated environment observation
            reward (float): Reward signal for the taken action
            terminated (bool): Whether the episode has ended
            truncated (bool): Whether the episode was truncated
            info (dict): Additional information
        """
        reward = 0
        self.current_step += 1
        
        # Process table: Each row is a process [RAM, CPU, Priority,State(1=Running,0.6=Suspended,0.3=Swapped, 0=Killed)]
        for i in range(self.k):
            process_action = action[i]
            reward += self.handlers[process_action](i)
        
        # Apply natural process dynamics (memory leaks, CPU fluctuations, random terminations)
        self._apply_process_dynamics()
        
        # Spawn new processes to replace killed ones
        self._spawn_new_process()
        
        self._update_system_stats()
        reward += self._calculate_global_reward()
        obs = self._get_obs()
        info = {
            "step": self.current_step,
            "ram_usage": float(self.system_stats[RAM_USAGE_INDEX]),
            "cpu_usage": float(self.system_stats[CPU_USAGE_INDEX]),
            "page_faults": float(self.system_stats[PAGE_FAULTS_INDEX]),
            "swap_usage": float(self.system_stats[SWAP_USAGE_INDEX]),
            "power": float(self.system_stats[POWER_INDEX])
        }
        terminated = self.system_stats[RAM_USAGE_INDEX] >= 1.0  # Terminate if RAM usage hits 100%
        
        return obs, reward, terminated, False, info
        
    def render(self):
        """
        Renders the current environment state using the selected visualization style.
        
        Supports multiple renderer styles:
        - 'cyberpunk': Neon-themed dashboard with glowing effects and scanlines
        - 'retro': Classic terminal with green text and ASCII art
        - 'anime': Pastel kawaii aesthetic with rounded corners
        
        The rendering only occurs when render_mode is set to 'human' during initialization.
        Renderer is lazily initialized on first render() call.
        """
        if self.render_mode != "human":
            return
            
        # Lazy initialize renderer on first call
        if self.renderer is None:
            from .renderers import CyberpunkRenderer, RetroTerminalRenderer, HyprlandAnimeRenderer
            
            if self.renderer_style == 'retro':
                self.renderer = RetroTerminalRenderer(self, self.window_size)
            elif self.renderer_style == 'anime' or self.renderer_style == 'hyprland':
                self.renderer = HyprlandAnimeRenderer(self, self.window_size)
            else:  # default to cyberpunk
                self.renderer = CyberpunkRenderer(self, self.window_size)
                
            self.renderer.initialize()
        
        # Delegate rendering to the renderer
        self.renderer.render()
    
    def close(self):
        """
        Safely closes the rendering window and releases all graphics resources.
        
        Delegates cleanup to the renderer if one is active.
        """
        if self.renderer is not None:
            self.renderer.close()
            self.renderer = None
