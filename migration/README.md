# MyShell_RFD v2.0

Professional, modular configuration tool for ZSH environments.

## Features

- **Modern TUI**: Beautiful terminal interface built with Textual
- **ZSH Focused**: Optimized for ZSH with Oh My Zsh integration
- **22+ Tool Modules**: AWS, Kubectl, Docker, Terraform, and more
- **Profile Management**: Switch between work, personal, and custom profiles
- **Rollback System**: Safely revert configuration changes
- **Offline Mode**: Cache installers for offline use
- **Plugin System**: Extend with custom modules

## Installation

### Using uv (Recommended)

```bash
# Install uv if not present
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Using pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

### Interactive Mode (TUI)

```bash
# Run without arguments to launch interactive TUI
myshell
```

### CLI Mode

```bash
# List available modules
myshell list

# Install specific module
myshell install aws
myshell install kubectl

# List available modules
myshell list

# Show module info
myshell info kubectl

# Manage profiles
myshell profile list
myshell profile switch work
myshell profile export backup.toml

# Rollback changes
myshell rollback list
myshell rollback apply <snapshot-id>

# Update
myshell update

# Clean configuration
myshell clean
```

### Options

```bash
# Auto-accept all prompts
myshell --yes install

# Offline mode
myshell --offline install kubectl

# Use specific profile
myshell --profile work install
```

## Configuration

Configuration is stored in `~/.myshell_rfd/`:

```
~/.myshell_rfd/
├── config.toml          # Main configuration
├── profiles/            # Named profiles
│   ├── default.toml
│   ├── work.toml
│   └── personal.toml
├── cache/               # Offline cache
├── backups/             # Rollback snapshots
└── plugins/             # External plugins
```

## Development

```bash
# Run tests
uv run pytest tests/ -v

# Run tests with coverage
uv run pytest tests/ -v --cov=src/myshell_rfd --cov-report=term-missing

# Linting
uv run ruff check src/ tests/

# Format code
uv run ruff format src/ tests/
```

## Building Binary

The build script uses Docker/Podman to create a portable binary compatible with
RHEL 9+ and Ubuntu 24.04+. This ensures glibc compatibility across distributions.

```bash
# Build using container (recommended - portable binary)
python scripts/build.py

# Build locally (uses system glibc - less portable)
python scripts/build.py --local

# Clean build artifacts
python scripts/build.py --clean

# Force specific container runtime
python scripts/build.py --runtime docker
python scripts/build.py --runtime podman
```

### Binary Compatibility

The containerized build uses Debian 11 (glibc 2.31) as base, ensuring
compatibility with:
- RHEL 9+ (glibc 2.34)
- Ubuntu 24.04+ (glibc 2.39)
- Any Linux distribution with glibc >= 2.31

## License

Proprietary - All rights reserved.
