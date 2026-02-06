# Installation Guide

## Requirements

- Python 3.8 or higher
- pip package manager

## Standard Installation

### From Source

1. Clone the repository (or download the source):
```bash
git clone https://github.com/yourusername/ramsim.git
cd ramsim
```

2. Install in development mode:
```bash
pip install -e .
```

This will install RamSim along with all required dependencies.

### Dependencies

The following packages will be automatically installed:
- `gymnasium>=0.28.0` - OpenAI Gym API
- `numpy>=1.21.0` - Numerical computing
- `pygame>=2.1.0` - Visualization rendering

## Optional Dependencies

### Development Tools

For development and testing:
```bash
pip install -e ".[dev]"
```

This includes:
- pytest - Testing framework
- pytest-cov - Code coverage
- black - Code formatter
- flake8 - Linter
- mypy - Type checker

Or install from requirements-dev.txt:
```bash
pip install -r requirements-dev.txt
```

### Reinforcement Learning

For training RL agents:
```bash
pip install -e ".[rl]"
```

This includes:
- stable-baselines3 - RL algorithms
- torch - Deep learning framework

## Verify Installation

Test your installation:

```python
import ramsim
from ramsim import RamSimEnv

# Create environment
env = RamSimEnv(k=5)
obs, info = env.reset()

print("✓ RamSim installed successfully!")
print(f"  Version: {ramsim.__version__}")
print(f"  Number of processes: {env.k}")
```

## Virtual Environment (Recommended)

It's recommended to use a virtual environment:

### Using venv

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install RamSim
pip install -e .
```

### Using conda

```bash
# Create conda environment
conda create -n ramsim python=3.10

# Activate
conda activate ramsim

# Install RamSim
pip install -e .
```

## Troubleshooting

### Pygame Installation Issues

If pygame fails to install:

**Windows:**
```bash
pip install pygame --pre
```

**Linux:**
```bash
# Install SDL dependencies first
sudo apt-get install python3-dev python3-numpy libsdl-image1.2-dev \
    libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libsdl1.2-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev

pip install pygame
```

**Mac:**
```bash
brew install sdl2 sdl2_image sdl2_ttf sdl2_mixer portmidi
pip install pygame
```

### Import Errors

If you get import errors, make sure you're in the virtual environment and have installed the package:
```bash
pip show ramsim
```

If not installed:
```bash
pip install -e .
```

### Visualization Issues

If visualization doesn't work:

1. Check pygame installation:
```python
import pygame
print(pygame.ver)
```

2. Test basic pygame:
```python
import pygame
pygame.init()
screen = pygame.display.set_mode((640, 480))
print("✓ Pygame working!")
pygame.quit()
```

## Uninstallation

To uninstall RamSim:
```bash
pip uninstall ramsim
```
