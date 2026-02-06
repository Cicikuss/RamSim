"""
Basic usage example for RamSim environment.

This script demonstrates the simplest way to use RamSim in headless mode.
"""
from ramsim import RamSimEnv


def main():
    """Run basic RamSim example."""
    print("=" * 60)
    print("RamSim - Basic Usage Example")
    print("=" * 60)
    
    # Create environment with 5 processes
    env = RamSimEnv(k=5)
    print(f"\n✓ Created environment with {env.k} processes")
    
    # Reset environment
    obs, info = env.reset(seed=42)
    print(f"✓ Environment reset - Status: {info['status']}")
    
    # Print initial state
    print(f"\nInitial System Stats:")
    print(f"  RAM Usage:    {obs['system_stats'][0]:.2%}")
    print(f"  CPU Usage:    {obs['system_stats'][1]:.2%}")
    print(f"  Page Faults:  {obs['system_stats'][2]:.3f}")
    print(f"  Swap Usage:   {obs['system_stats'][3]:.2%}")
    print(f"  Power:        {obs['system_stats'][4]:.2%}")
    
    print(f"\nProcess Table (first 3 processes):")
    print("  PID | RAM    | CPU    | Priority | State")
    print("  " + "-" * 45)
    for i in range(min(3, env.k)):
        ram, cpu, prio, state = obs['process_table'][i]
        state_name = "RUN" if state == 1.0 else "SLP" if state == 0.6 else "SWP" if state == 0.3 else "KILL"
        print(f"  {i:3d} | {ram:6.3f} | {cpu:6.3f} | {prio:8.3f} | {state_name}")
    
    # Run for 10 steps with random actions
    print(f"\n{'=' * 60}")
    print("Running 10 random steps...")
    print(f"{'=' * 60}\n")
    
    total_reward = 0
    for step in range(10):
        # Sample random action
        action = env.action_space.sample()
        
        # Take step
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        print(f"Step {step + 1:2d} | "
              f"RAM: {info['ram_usage']:5.1%} | "
              f"CPU: {info['cpu_usage']:5.1%} | "
              f"Reward: {reward:7.2f}")
        
        if terminated:
            print("\n⚠ Episode terminated (RAM overflow)")
            break
    
    print(f"\n{'=' * 60}")
    print(f"Total Reward: {total_reward:.2f}")
    print(f"Final RAM Usage: {info['ram_usage']:.2%}")
    print(f"{'=' * 60}")
    
    # Clean up
    env.close()
    print("\n✓ Environment closed")


if __name__ == "__main__":
    main()
