# Contributing to RamSim

Thank you for your interest in contributing to RamSim! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear description of the problem
- Steps to reproduce the issue
- Expected vs. actual behavior
- Your environment (OS, Python version, RamSim version)

### Suggesting Enhancements

We welcome feature requests! Please create an issue with:
- A clear description of the enhancement
- Use cases and examples
- Why this would be useful to other users

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run tests (`pytest tests/`)
5. Format code (`black src/ramsim tests examples`)
6. Commit your changes (`git commit -m 'Add some feature'`)
7. Push to the branch (`git push origin feature/your-feature`)
8. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/ramsim.git
cd ramsim

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Check formatting
black --check src/ramsim tests examples

# Run linter
flake8 src/ramsim
```

## Code Style

- We use [Black](https://black.readthedocs.io/) for code formatting (line length: 100)
- We use [flake8](https://flake8.pycqa.org/) for linting
- Write docstrings for all public functions/classes
- Add type hints where appropriate

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage
- Test on multiple Python versions if possible

## Commit Messages

- Use clear and descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Keep first line under 72 characters
- Add detailed description if needed

Example:
```
Add support for custom reward functions

- Implement RewardWrapper class
- Add tests for custom rewards
- Update documentation
```

## Code of Conduct

Be respectful and inclusive. We're all here to learn and improve.

## Questions?

Feel free to open an issue for any questions about contributing!
