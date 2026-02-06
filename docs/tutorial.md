# RamSim Tutorial

Complete tutorial for getting started with RamSim.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Understanding Observations](#understanding-observations)
3. [Taking Actions](#taking-actions)
4. [Visualization](#visualization)
5. [Training RL Agents](#training-rl-agents)
6. [Advanced Usage](#advanced-usage)

---

## Basic Usage

### Creating an Environment

```python
from ramsim import RamSimEnv

# Create environment with 5 processes
env = RamSimEnv(k=5)

# Reset to get initial observation
obs, info = env.reset(seed=42)
```

### Running a Simple Loop

```python
for step in range(100):
    # Sample a random action
    action = env.action_space.sample()
    
    # Take a step
    obs, reward, terminated, truncated, info = env.step(action)
    
    # Print status
    print(f"Step {step}: RAM={info['ram_usage']:.1%}, Reward={reward:.2f}")
    
    # Reset if episode ends
    if terminated or truncated:
        obs, info = env.reset()

env.close()
```

---

## Understanding Observations

The observation is a dictionary with two components:

### System Stats

```python
system_stats = obs['system_stats']
# [RAM usage, CPU usage, Page faults, Swap usage, Power consumption]

ram_usage = system_stats[0]  # 0-1
cpu_usage = system_stats[1]  # 0-1
page_faults = system_stats[2]  # 0-1
swap_usage = system_stats[3]  # 0-1
power = system_stats[4]  # 0-1
```

### Process Table

```python
process_table = obs['process_table']  # Shape: (k, 4)

# For each process:
for i in range(env.k):
    ram = process_table[i, 0]      # RAM usage
    cpu = process_table[i, 1]      # CPU usage
    priority = process_table[i, 2]  # Priority level
    state = process_table[i, 3]     # Process state
    
    # Decode state
    if state == 1.0:
        print(f"Process {i}: Running")
    elif state == 0.6:
        print(f"Process {i}: Suspended")
    elif state == 0.3:
        print(f"Process {i}: Swapped")
    elif state == 0.0:
        print(f"Process {i}: Killed")
```

---

## Taking Actions

### Action Types

Each action is a list of length k, with one action per process:

```python
from ramsim import ACTION_KILL, ACTION_NOOP, ACTION_SWAP_OUT

# Kill first process, leave others alone
action = [ACTION_KILL, ACTION_NOOP, ACTION_NOOP, ACTION_NOOP, ACTION_NOOP]
obs, reward, terminated, truncated, info = env.step(action)
```

### All Available Actions

```python
from ramsim import (
    ACTION_KILL,           # 0 - Terminate process
    ACTION_SWAP_OUT,       # 1 - Move to swap space
    ACTION_SWAP_IN,        # 2 - Bring back from swap
    ACTION_SUSPEND,        # 3 - Pause process
    ACTION_RESUME,         # 4 - Resume paused process
    ACTION_RENICE_INCREASE,# 5 - Increase priority
    ACTION_RENICE_DECREASE,# 6 - Decrease priority
    ACTION_NOOP           # 7 - Do nothing
)
```

### Smart Action Selection

Example: Kill memory leaks

```python
def find_memory_leaks(process_table):
    """Find processes with high RAM but low CPU (likely leaks)."""
    leaky_processes = []
    for i in range(len(process_table)):
        ram, cpu, priority, state = process_table[i]
        if ram > 0.6 and cpu < 0.1 and state == 1.0:
            leaky_processes.append(i)
    return leaky_processes

# Use it
action = [ACTION_NOOP] * env.k
leaky = find_memory_leaks(obs['process_table'])
for idx in leaky:
    action[idx] = ACTION_KILL

obs, reward, _, _, _ = env.step(action)
```

---

## Visualization

### Cyberpunk Style

```python
env = RamSimEnv(k=5, render_mode='human', renderer_style='cyberpunk')
env.reset()

for _ in range(100):
    action = env.action_space.sample()
    obs, _, terminated, _, _ = env.step(action)
    env.render()  # Show visualization
    
    if terminated:
        env.reset()

env.close()
```

### Retro Terminal Style

```python
env = RamSimEnv(k=5, render_mode='human', renderer_style='retro')
```

### Anime/Kawaii Style

```python
env = RamSimEnv(k=5, render_mode='human', renderer_style='anime')
```

### Custom Window Size

```python
env = RamSimEnv(
    k=10,
    render_mode='human',
    renderer_style='cyberpunk',
    window_size=(1920, 1080)  # Custom size
)
```

---

## Training RL Agents

### Using Stable-Baselines3

```python
from stable_baselines3 import PPO
from ramsim import RamSimEnv

# Create environment
env = RamSimEnv(k=5)

# Create PPO agent
model = PPO("MultiInputPolicy", env, verbose=1)

# Train for 100k steps
model.learn(total_timesteps=100_000)

# Save model
model.save("ramsim_ppo")

# Load and test
model = PPO.load("ramsim_ppo")
obs = env.reset()
for _ in range(100):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, _, info = env.step(action)
    if done:
        obs = env.reset()
```

### Parallel Training

```python
from stable_baselines3.common.env_util import make_vec_env

# Create 4 parallel environments
env = make_vec_env(lambda: RamSimEnv(k=5), n_envs=4)

# Train with parallel environments
model = PPO("MultiInputPolicy", env, verbose=1)
model.learn(total_timesteps=500_000)
```

---

## Advanced Usage

### Custom Reward Function

You can create a wrapper to modify rewards:

```python
import gymnasium as gym

class CustomRewardWrapper(gym.Wrapper):
    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)
        
        # Custom reward logic
        ram_usage = info['ram_usage']
        if ram_usage > 0.9:
            reward -= 100  # Heavy penalty for high RAM
        
        return obs, reward, terminated, truncated, info

# Use it
env = CustomRewardWrapper(RamSimEnv(k=5))
```

### Monitoring with Gymnasium Wrappers

```python
from gymnasium.wrappers import RecordEpisodeStatistics, RecordVideo

env = RamSimEnv(k=5, render_mode='human')
env = RecordEpisodeStatistics(env)
env = RecordVideo(env, 'videos/')
```

### Process Profiles

Understanding different process types:

```python
# Heavy Process: High CPU + High RAM
# - RAM: 0.4-0.6
# - CPU: 0.6-0.9
# - Priority: 0.7-1.0
# Action: Keep running if priority is high

# Memory Leak: High RAM + Low CPU
# - RAM: 0.6-0.8
# - CPU: 0.0-0.05
# - Priority: 0.0-0.2
# Action: Kill or swap out

# Active Process: Normal usage
# - RAM: 0.1-0.4
# - CPU: 0.2-0.5
# - Priority: 0.4-0.7
# Action: Manage based on system load

# Idle Process: Minimal usage
# - RAM: 0.01-0.05
# - CPU: 0.0-0.02
# - Priority: 0.1-0.4
# Action: Safe to suspend if needed
```

### Experiment Tracking

```python
import json

class ExperimentLogger:
    def __init__(self, filename):
        self.filename = filename
        self.data = []
    
    def log_step(self, step, action, obs, reward, info):
        self.data.append({
            'step': step,
            'action': action.tolist(),
            'ram_usage': info['ram_usage'],
            'cpu_usage': info['cpu_usage'],
            'reward': reward
        })
    
    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)

# Use it
logger = ExperimentLogger('experiment.json')
env = RamSimEnv(k=5)
obs, _ = env.reset()

for step in range(100):
    action = env.action_space.sample()
    obs, reward, _, _, info = env.step(action)
    logger.log_step(step, action, obs, reward, info)

logger.save()
```

---

## Next Steps

- Check out the [API Reference](api.md) for detailed documentation
- Explore the `examples/` directory for more code samples
- Read the source code in `src/ramsim/` to understand internals
- Join our community and contribute!
