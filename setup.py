"""
Setup script for RamSim package.
For modern installations, prefer using pyproject.toml with pip install.
This file is provided for backward compatibility.
"""
from setuptools import setup, find_packages
import os

# Read the long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ramsim",
    version="1.0.0",
    author="RamSim Contributors",
    description="A Gymnasium-based RAM Management Simulation Environment for Reinforcement Learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ramsim",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/ramsim/issues",
        "Documentation": "https://github.com/yourusername/ramsim#readme",
        "Source Code": "https://github.com/yourusername/ramsim",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "gymnasium>=0.28.0",
        "numpy>=1.21.0",
        "pygame>=2.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "rl": [
            "stable-baselines3>=2.0.0",
            "torch>=2.0.0",
        ],
    },
    keywords="reinforcement-learning gymnasium ram-management operating-systems simulation",
)
