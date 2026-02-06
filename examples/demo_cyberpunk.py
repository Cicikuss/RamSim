"""
Cyberpunk visualization demo for RamSim.

This script demonstrates the Cyberpunk-themed visualization style.
Press ESC or close the window to exit.
"""
import time
from ramsim import RamSimEnv


def main():
    """Run cyberpunk visualization demo."""
    print("=" * 60)
    print("RamSim - Cyberpunk Visualization Demo")
    print("=" * 60)
    print("\n🎮 Controls:")
    print("  - Close window or press ESC to exit")
    print("  - The environment will take random actions automatically")
    print("\nStarting in 2 seconds...")
    time.sleep(2)
    
    # Create environment with cyberpunk visualization
    env = RamSimEnv(
        k=5,
        render_mode='human',
        renderer_style='cyberpunk'
    )
    
    # Reset and start
    obs, info = env.reset(seed=42)
    
    try:
        step = 0
        running = True
        
        while running:
            # Take random action
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            
            # Render
            env.render()
            
            step += 1
            
            # Print status every 10 steps
            if step % 10 == 0:
                print(f"Step {step:3d} | "
                      f"RAM: {info['ram_usage']:5.1%} | "
                      f"CPU: {info['cpu_usage']:5.1%} | "
                      f"Reward: {reward:7.2f}")
            
            if terminated:
                print("\n⚠ Episode terminated - Restarting...")
                obs, info = env.reset()
                step = 0
            
            # Slow down rendering for better visualization
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\n\n✓ Interrupted by user")
    finally:
        env.close()
        print("✓ Environment closed")


if __name__ == "__main__":
    main()
