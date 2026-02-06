"""
Reinforcement Learning training example using Stable-Baselines3.

This script shows how to train an RL agent on RamSim using PPO.
Requires: pip install stable-baselines3
"""
try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.env_util import make_vec_env
    from stable_baselines3.common.callbacks import EvalCallback
    SB3_AVAILABLE = True
except ImportError:
    SB3_AVAILABLE = False
    print("⚠ stable-baselines3 not installed. Install with: pip install stable-baselines3")

from ramsim import RamSimEnv


def main():
    """Train a PPO agent on RamSim."""
    if not SB3_AVAILABLE:
        print("\nPlease install stable-baselines3 to run this example:")
        print("  pip install stable-baselines3")
        return
    
    print("=" * 60)
    print("RamSim - RL Training Example with PPO")
    print("=" * 60)
    
    # Create vectorized environment (4 parallel environments)
    print("\n📊 Creating training environment...")
    env = make_vec_env(
        lambda: RamSimEnv(k=5),
        n_envs=4,
        seed=42
    )
    
    # Create evaluation environment
    eval_env = RamSimEnv(k=5)
    
    # Setup evaluation callback
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path='./models/',
        log_path='./logs/',
        eval_freq=5000,
        deterministic=True,
        render=False
    )
    
    print("✓ Environment created")
    
    # Create PPO agent
    print("\n🤖 Creating PPO agent...")
    model = PPO(
        "MultiInputPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        tensorboard_log="./tensorboard/",
    )
    print("✓ Agent created")
    
    # Train the agent
    print("\n🎯 Starting training...")
    print("  Total timesteps: 100,000")
    print("  Evaluation frequency: every 5,000 steps")
    print("\nPress Ctrl+C to stop training early\n")
    
    try:
        model.learn(
            total_timesteps=100_000,
            callback=eval_callback,
            progress_bar=True
        )
        
        print("\n✓ Training completed!")
        
        # Save final model
        model.save("ramsim_ppo_final")
        print("✓ Model saved as 'ramsim_ppo_final.zip'")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Training interrupted by user")
        model.save("ramsim_ppo_interrupted")
        print("✓ Model saved as 'ramsim_ppo_interrupted.zip'")
    
    # Test the trained agent
    print("\n🧪 Testing trained agent...")
    obs = eval_env.reset()
    total_reward = 0
    
    for step in range(100):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = eval_env.step(action)
        total_reward += reward
        
        if step % 10 == 0:
            print(f"Step {step:3d} | "
                  f"RAM: {info['ram_usage']:5.1%} | "
                  f"CPU: {info['cpu_usage']:5.1%} | "
                  f"Reward: {reward:7.2f}")
        
        if terminated or truncated:
            print(f"\nEpisode ended at step {step}")
            break
    
    print(f"\n{'=' * 60}")
    print(f"Total Reward: {total_reward:.2f}")
    print(f"{'=' * 60}")
    
    # Clean up
    env.close()
    eval_env.close()
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
