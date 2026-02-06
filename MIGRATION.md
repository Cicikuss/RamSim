# Migration Guide: Old Structure → Professional Structure

This guide helps you transition from the old flat structure to the new professional package structure.

## What Changed?

### Old Structure (Before)
```
RamSim/
├── RamSim.py          # Everything in one file
├── renderers.py       # All renderers in one file
├── README.md
└── requirements.txt
```

### New Structure (After)
```
RamSim/
├── src/ramsim/              # Organized source code
│   ├── __init__.py
│   ├── environment.py       # RamSimEnv class
│   ├── renderers/          # Renderer modules
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── cyberpunk.py
│   │   ├── retro.py
│   │   └── anime.py
│   └── utils/              # Constants and utilities
│       ├── __init__.py
│       └── constants.py
├── tests/                   # Test suite
│   ├── test_environment.py
│   ├── test_renderers.py
│   └── test_integration.py
├── examples/               # Example scripts
│   ├── basic_usage.py
│   ├── demo_cyberpunk.py
│   ├── demo_retro.py
│   ├── demo_anime.py
│   └── train_agent.py
├── docs/                   # Documentation
│   ├── api.md
│   ├── installation.md
│   └── tutorial.md
├── .github/workflows/      # CI/CD
│   └── tests.yml
├── setup.py               # Package setup
├── pyproject.toml         # Modern Python packaging
├── LICENSE                # MIT License
├── CHANGELOG.md           # Version history
└── CONTRIBUTING.md        # Contribution guidelines
```

## How to Migrate Your Code

### Import Changes

**Old way:**
```python
from RamSim import RamSimEnv
from renderers import CyberpunkRenderer
```

**New way:**
```python
from ramsim import RamSimEnv
from ramsim.renderers import CyberpunkRenderer
```

### Using Constants

**Old way:**
```python
RAM_USAGE_INDEX = 0  # Had to define manually or import from RamSim
```

**New way:**
```python
from ramsim import RAM_USAGE_INDEX, CPU_USAGE_INDEX, ACTION_KILL, ACTION_NOOP
```

## Installation

### Old Way
```bash
# Just installed dependencies
pip install -r requirements.txt

# Had to manually add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### New Way
```bash
# Proper package installation
pip install -e .

# Or for development
pip install -e ".[dev]"
```

## Old Files Cleanup (Optional)

After migration, you can safely archive these old files:

```bash
# Create backup directory
mkdir old_structure_backup

# Move old files
mv RamSim.py old_structure_backup/
mv renderers.py old_structure_backup/
```

**Note:** DO NOT delete these until you've verified everything works with the new structure!

## Benefits of New Structure

1. **Proper Package**: Can be installed with pip
2. **Better Organization**: Code split into logical modules
3. **Testing**: Comprehensive test suite included
4. **Documentation**: Structured docs in `docs/` folder
5. **CI/CD**: Automated testing with GitHub Actions
6. **Examples**: Ready-to-run example scripts
7. **Type Safety**: Better IDE support and type hints
8. **Maintainability**: Easier to find and fix bugs
9. **Professional**: Industry-standard project structure
10. **Distribution**: Can be published to PyPI

## Verification Steps

1. **Install the package:**
   ```bash
   pip install -e .
   ```

2. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

3. **Try an example:**
   ```bash
   python examples/basic_usage.py
   ```

4. **Test imports:**
   ```python
   from ramsim import RamSimEnv
   env = RamSimEnv(k=5)
   print("✓ Migration successful!")
   ```

## Troubleshooting

### Import Error: "No module named 'ramsim'"

**Solution:** Install the package in development mode:
```bash
pip install -e .
```

### Old code still using "from RamSim import"

**Solution:** Update imports to use lowercase `ramsim`:
```bash
# Find all occurrences
grep -r "from RamSim import" .

# Update manually or use sed
sed -i 's/from RamSim import/from ramsim import/g' your_file.py
```

### Tests failing

**Solution:** Make sure dev dependencies are installed:
```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Need Help?

- Check [Installation Guide](docs/installation.md)
- Read [Tutorial](docs/tutorial.md)
- Open an [Issue](https://github.com/yourusername/ramsim/issues)
