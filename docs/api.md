# API Reference

## RamSimEnv

The main environment class for RamSim.

### Constructor

```python
RamSimEnv(k=5, render_mode=None, renderer_style='cyberpunk', window_size=None)
```

**Parameters:**
- `k` (int): Number of processes to monitor in the system (default: 5)
- `render_mode` (str): Rendering mode - 'human' for visualization, None for headless
- `renderer_style` (str): Visual theme - 'cyberpunk', 'retro', or 'anime' (default: 'cyberpunk')
- `window_size` (tuple): Window size (width, height). If None, auto-calculated based on k

### Methods

#### `reset(seed=None, options=None)`

Resets the environment to a non-deterministic initial state.

**Parameters:**
- `seed` (int, optional): Random seed for reproducibility
- `options` (dict, optional): Additional options

**Returns:**
- `observation` (dict): Initial observation with 'system_stats' and 'process_table'
- `info` (dict): Additional information

#### `step(action)`

Executes the given action on the processes and updates the environment state.

**Parameters:**
- `action` (list): List of actions for each process (length k)

**Returns:**
- `observation` (dict): Updated environment observation
- `reward` (float): Reward signal for the taken action
- `terminated` (bool): Whether the episode has ended
- `truncated` (bool): Whether the episode was truncated
- `info` (dict): Additional information about system metrics

#### `render()`

Renders the current environment state using the selected visualization style.

#### `close()`

Safely closes the rendering window and releases all graphics resources.

### Action Space

MultiDiscrete space with 8 possible actions for each process:

- **0 - Kill**: Terminate the process
- **1 - Swap Out**: Move process to swap space
- **2 - Swap In**: Bring process back from swap space
- **3 - Suspend**: Pause the process
- **4 - Resume**: Resume a suspended process
- **5 - Renice Increase**: Increase process priority
- **6 - Renice Decrease**: Decrease process priority
- **7 - NoOp**: Do nothing

### Observation Space

Dictionary with:

```python
{
    "system_stats": Box(low=0, high=1, shape=(5,), dtype=float32),
    "process_table": Box(low=0, high=1, shape=(k, 4), dtype=float32)
}
```

**system_stats** contains:
- `[0]`: RAM usage (0-1)
- `[1]`: CPU usage (0-1)
- `[2]`: Page faults (0-1)
- `[3]`: Swap usage (0-1)
- `[4]`: Power consumption (0-1)

**process_table** contains for each process:
- `[:,0]`: RAM usage
- `[:,1]`: CPU usage
- `[:,2]`: Priority
- `[:,3]`: State (1.0=Running, 0.6=Suspended, 0.3=Swapped, 0.0=Killed)

### Reward Structure

The environment provides rewards based on:

1. **Action-specific rewards**: Each action has specific rewards/penalties
   - Killing memory leaks: +20
   - Killing critical processes: -10
   - Swapping under memory pressure: +10
   - Invalid actions: -2 to -5

2. **Global rewards**: System-wide metrics
   - Stability: -10 if RAM >= 90%, else +1
   - Power efficiency: (1 - power) × 2
   - Quality of Service: Sum of running high-priority processes
   - Thrashing penalty: -(swap_usage + page_faults) × 5

Final reward = action_rewards + (0.4×stability + 0.2×power + 0.3×qos + 0.1×thrashing)

---

## Constants

### System Stats Indices
```python
RAM_USAGE_INDEX = 0
CPU_USAGE_INDEX = 1
PAGE_FAULTS_INDEX = 2
SWAP_USAGE_INDEX = 3
POWER_INDEX = 4
```

### Process States
```python
STATE_RUNNING = 1.0
STATE_SUSPENDED = 0.6
STATE_SWAPPED = 0.3
STATE_KILLED = 0.0
```

### Actions
```python
ACTION_KILL = 0
ACTION_SWAP_OUT = 1
ACTION_SWAP_IN = 2
ACTION_SUSPEND = 3
ACTION_RESUME = 4
ACTION_RENICE_INCREASE = 5
ACTION_RENICE_DECREASE = 6
ACTION_NOOP = 7
```

---

## Renderers

### CyberpunkRenderer

Neon-themed dashboard with glowing effects and scanlines.

**Features:**
- Cyberpunk color scheme (cyan, magenta, neon)
- Glowing process bars
- Grid background with scanlines
- Glitch effects on text

### RetroTerminalRenderer

Classic green terminal with ASCII art.

**Features:**
- Pure black background with green text
- ASCII-style progress bars
- Blinking cursor
- Monospace font

### HyprlandAnimeRenderer

Pastel kawaii aesthetic with rounded corners.

**Features:**
- Catppuccin-inspired color palette
- Rounded corners on all elements
- Floating particle effects
- Cute text labels (uwu, owo, nya)
