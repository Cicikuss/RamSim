"""
RamSim - RAM Management Simulation Environment for Reinforcement Learning.

A Gymnasium-based environment that simulates RAM management in an operating system,
enabling agents to learn resource management strategies through reinforcement learning.
"""

__version__ = "1.0.0"

from .environment import RamSimEnv
from .utils.constants import (
    RAM_USAGE_INDEX,
    CPU_USAGE_INDEX,
    PAGE_FAULTS_INDEX,
    SWAP_USAGE_INDEX,
    POWER_INDEX,
    STATE_RUNNING,
    STATE_SUSPENDED,
    STATE_SWAPPED,
    STATE_KILLED,
    ACTION_KILL,
    ACTION_SWAP_OUT,
    ACTION_SWAP_IN,
    ACTION_SUSPEND,
    ACTION_RESUME,
    ACTION_RENICE_INCREASE,
    ACTION_RENICE_DECREASE,
    ACTION_NOOP
)

__all__ = [
    'RamSimEnv',
    'RAM_USAGE_INDEX',
    'CPU_USAGE_INDEX',
    'PAGE_FAULTS_INDEX',
    'SWAP_USAGE_INDEX',
    'POWER_INDEX',
    'STATE_RUNNING',
    'STATE_SUSPENDED',
    'STATE_SWAPPED',
    'STATE_KILLED',
    'ACTION_KILL',
    'ACTION_SWAP_OUT',
    'ACTION_SWAP_IN',
    'ACTION_SUSPEND',
    'ACTION_RESUME',
    'ACTION_RENICE_INCREASE',
    'ACTION_RENICE_DECREASE',
    'ACTION_NOOP'
]
