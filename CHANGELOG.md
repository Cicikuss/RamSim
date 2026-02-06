# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-06

### Added
- Initial release of RamSim
- Core RAM management simulation environment
- Support for 8 process actions (Kill, Swap Out/In, Suspend/Resume, Renice, NoOp)
- Three visualization styles:
  - Cyberpunk: Neon-themed dashboard with glowing effects
  - Retro: Classic terminal with green text and ASCII art
  - Anime: Pastel kawaii aesthetic with rounded corners
- Dynamic process profiles (Heavy, Leaky, Active, Idle)
- Realistic reward system balancing stability, power, QoS, and thrashing
- Process dynamics simulation (memory leaks, CPU fluctuations, random terminations)
- Automatic process spawning to maintain system realism
- Dynamic window sizing based on renderer style
- Comprehensive test suite
- Example scripts for basic usage and RL training
- Full documentation

### Features
- 5 system metrics: RAM, CPU, Page Faults, Swap Space, Power Consumption
- Compatible with Gymnasium API
- Extensible renderer system
- Professional package structure with proper setup.py and pyproject.toml
- CI/CD pipeline with GitHub Actions

[1.0.0]: https://github.com/Cicikuss/ramsim/releases/tag/v1.0.0
