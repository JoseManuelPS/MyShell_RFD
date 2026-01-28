# AGENTS.md — MyShell_RFD

> Instructions for AI coding agents working on this project.
> Compatible with Cursor, Codex, Copilot, Aider, and other AGENTS.md-aware tools.

## Project Overview

**MyShell_RFD** is a professional ZSH configuration tool that provides:

- **22 installable modules** for CLI tools (AWS, Kubectl, Docker, Terraform, etc.)
- **Profile system** for switching between work/personal/custom configurations
- **Rollback system** with snapshot-based configuration recovery
- **Offline mode** with cached installers for air-gapped environments
- **Plugin system** for third-party extensions via entry points

**Target users**: DevOps engineers, SREs, developers who want consistent ZSH environments.

**Constraints**:
- ZSH only (no Bash, Fish, or other shells)
- Linux only (binary targets RHEL 9+, Ubuntu 24.04+)
- Python 3.12+ required for code and testing

---

## Setup Commands

```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install all dependencies (including dev)
uv pip install -e ".[dev]"

# Verify installation
uv run myshell --version
uv run myshell list
```

---

## Code Style

### Language & Formatting

- **Language**: All code, comments, docstrings, and documentation in English
- **Formatter**: ruff (line length 88, double quotes)
- **Import sorting**: ruff isort-compatible (stdlib → third-party → local)

### Type Hints (Required Everywhere)

```python
# Always use modern union syntax
def process(data: str | None = None) -> dict[str, Any]:
    ...

# Use collections.abc for abstract types
from collections.abc import Sequence, Mapping, Iterator

def filter_items(items: Sequence[str]) -> Iterator[str]:
    ...
```

### Docstrings (Google Style)

```python
def install_module(
    name: str,
    config_path: Path | None = None,
    *,
    force: bool = False,
) -> InstallResult:
    """Install a module by name.

    Writes configuration to the user's ZSH config file and registers
    the module as installed in the current profile.

    Args:
        name: Module identifier (case-insensitive).
        config_path: Override default config file path.
        force: Reinstall even if already configured.

    Returns:
        InstallResult with success status and message.

    Raises:
        ModuleNotFoundError: If module doesn't exist in registry.
        PermissionError: If config file is not writable.

    Example:
        >>> result = install_module("aws", force=True)
        >>> print(result.message)
        'AWS CLI configured successfully'
    """
```

### Error Handling

```python
# GOOD: Specific exceptions with context
try:
    config = AppConfig.from_toml(path)
except FileNotFoundError:
    logger.info(f"No config at {path}, using defaults")
    config = AppConfig()
except tomli.TOMLDecodeError as e:
    raise ConfigError(f"Invalid TOML in {path}: {e}") from e

# BAD: Never do this
try:
    something()
except Exception:  # Too broad
    pass  # Silent failure
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `ModuleRegistry`, `InstallResult` |
| Functions/methods | snake_case | `install_module`, `get_config_path` |
| Constants | UPPER_SNAKE | `CONFIG_DIR`, `DEFAULT_PROFILE` |
| Private | Leading underscore | `_validate_input`, `_cache` |
| Module files | snake_case | `module_base.py`, `shell_plugins.py` |

---

## Testing Instructions

### Running Tests

```bash
# Full test suite
uv run pytest tests/ -v

# With coverage report
uv run pytest tests/ -v --cov=src/myshell_rfd --cov-report=term-missing

# Single test file
uv run pytest tests/test_core/test_config.py -v

# Single test by name pattern
uv run pytest tests/ -v -k "test_install"

# Stop on first failure
uv run pytest tests/ -v -x
```

### Writing Tests

```python
# tests/test_modules/test_new_module.py
import pytest
from pathlib import Path
from myshell_rfd.modules.new_module import NewModule


class TestNewModule:
    """Tests for NewModule."""

    def test_info_has_required_fields(self):
        """Verify module info contains all required metadata."""
        module = NewModule()
        info = module.info

        assert info.name == "newmodule"
        assert info.binary is not None
        assert info.category is not None

    def test_config_content_is_valid_shell(self, tmp_path: Path):
        """Verify generated config is valid shell syntax."""
        module = NewModule()
        content = module.get_config_content()

        # Must not be empty
        assert content.strip()
        # Must contain the module marker
        assert "newmodule" in content.lower() or info.binary in content

    def test_install_creates_config(self, tmp_path: Path, mock_shell):
        """Verify install writes to config file."""
        config_file = tmp_path / ".zshrc"
        config_file.touch()

        module = NewModule()
        result = module.install(config_file)

        assert result.success
        assert module.info.name in config_file.read_text()
```

### Test Fixtures (in conftest.py)

```python
@pytest.fixture
def temp_config(tmp_path: Path) -> Path:
    """Temporary .zshrc file."""
    config = tmp_path / ".zshrc"
    config.write_text("# Test config\n")
    return config

@pytest.fixture
def mock_shell(monkeypatch, tmp_path: Path):
    """Mock shell environment paths."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("ZSH_CUSTOM", str(tmp_path / ".oh-my-zsh/custom"))
    (tmp_path / ".oh-my-zsh/custom/plugins").mkdir(parents=True)
    return tmp_path
```

---

## Architecture

### Directory Structure

```
src/myshell_rfd/
├── __init__.py          # Package version, public exports
├── __main__.py          # Entry: python -m myshell_rfd
├── cli.py               # Typer CLI application
│
├── core/                # Business logic (UI-agnostic)
│   ├── config.py        # Pydantic models: AppConfig, ProfileConfig
│   ├── module_base.py   # BaseModule, ConfigOnlyModule, GitCloneModule
│   ├── registry.py      # Module discovery and lifecycle
│   ├── installer.py     # Installation orchestrator
│   ├── rollback.py      # Snapshot management
│   └── shell.py         # ZSH/Oh-My-Zsh operations
│
├── modules/             # Installable modules (one class per tool)
│   ├── __init__.py      # BUILTIN_MODULES list
│   ├── aws.py           # AWSModule
│   ├── containers.py    # DockerModule, PodmanModule
│   ├── kubernetes.py    # KubectlModule, HelmModule, MinikubeModule, etc.
│   ├── cloud.py         # TerraformModule, RosaModule, EksctlModule
│   ├── tools.py         # FZFModule, BatcatModule, PLSModule, NVMModule
│   ├── vcs.py           # GitModule, GitHubModule
│   ├── shell_plugins.py # ZshAutosuggestionsModule, ZshSyntaxHighlightingModule
│   └── themes.py        # PowerLevel10KModule
│
├── plugins/             # External plugin system
│   ├── __init__.py      # Plugin documentation
│   ├── loader.py        # Entry point and directory-based discovery
│   └── example.py       # Template for custom plugins
│
├── tui/                 # Textual TUI application
│   ├── app.py           # Main Textual App
│   ├── screens/         # MainScreen, SettingsScreen, HelpScreen
│   └── widgets/         # ModuleCard, ProgressPanel, StatusBar
│
└── utils/               # Shared utilities
    ├── logger.py        # Rich-based colored logging
    ├── files.py         # Safe file ops with backup
    ├── process.py       # Subprocess wrappers
    └── detect.py        # Binary detection, version parsing
```

### Data Flow

```
User Command
     │
     ▼
┌─────────┐     ┌──────────┐     ┌──────────────┐
│   CLI   │────▶│ Registry │────▶│ BaseModule   │
│ (Typer) │     │          │     │ .install()   │
└─────────┘     └──────────┘     └──────────────┘
     │                                  │
     │                                  ▼
     │                          ┌──────────────┐
     │                          │ FileOps      │
     │                          │ .add_to_     │
     │                          │  config()    │
     │                          └──────────────┘
     │                                  │
     ▼                                  ▼
┌─────────┐                     ┌──────────────┐
│ AppConfig│◀────────────────────│ ~/.myshell_  │
│ (Pydantic)                    │ rfd/config.  │
└─────────┘                     │ zsh          │
                                └──────────────┘
```

### Key Classes

| Class | Responsibility |
|-------|---------------|
| `AppConfig` | Load/save TOML config, manage profiles |
| `ProfileConfig` | Track enabled modules per profile |
| `ModuleRegistry` | Discover, register, lookup modules |
| `BaseModule` | Abstract interface all modules implement |
| `ConfigOnlyModule` | Base for modules that only write config |
| `GitCloneModule` | Base for modules that clone repositories |
| `RollbackManager` | Create/restore configuration snapshots |
| `InstallerService` | Orchestrate installations with rollback |
| `ShellManager` | ZSH-specific operations (Oh-My-Zsh, themes) |

---

## Module Implementation Patterns

### Pattern 1: Config-Only Module

For tools that only need shell aliases/exports:

```python
from myshell_rfd.core.module_base import (
    ConfigOnlyModule,
    ModuleInfo,
    ModuleCategory,
)


class MyToolModule(ConfigOnlyModule):
    """Configuration for MyTool CLI."""

    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="mytool",
            display_name="MyTool",
            description="Productivity tool for developers",
            category=ModuleCategory.TOOLS,
            binary="mytool",  # Required binary in PATH
            url="https://mytool.dev",
            tags=["cli", "productivity"],
        )

    def get_config_content(self) -> str:
        return '''
# MyTool configuration
export MYTOOL_HOME="$HOME/.mytool"
export PATH="$MYTOOL_HOME/bin:$PATH"

alias mt="mytool"
alias mtr="mytool run"
'''
```

### Pattern 2: Git Clone Module

For tools installed by cloning a repository:

```python
from pathlib import Path
from myshell_rfd.core.module_base import (
    GitCloneModule,
    ModuleInfo,
    ModuleCategory,
)


class MyPluginModule(GitCloneModule):
    """ZSH plugin installed via git clone."""

    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="myplugin",
            display_name="My Plugin",
            description="Enhances ZSH with features",
            category=ModuleCategory.SHELL,
            tags=["zsh", "plugin"],
        )

    @property
    def repo_url(self) -> str:
        return "https://github.com/user/myplugin.git"

    @property
    def clone_path(self) -> Path:
        return Path.home() / ".oh-my-zsh/custom/plugins/myplugin"

    def get_config_content(self) -> str:
        return f'source "{self.clone_path}/myplugin.zsh"'
```

### Pattern 3: Module with Custom Install Logic

```python
from myshell_rfd.core.module_base import (
    BaseModule,
    ModuleInfo,
    ModuleCategory,
    InstallResult,
)
from myshell_rfd.utils.process import run


class ComplexModule(BaseModule):
    """Module requiring custom installation steps."""

    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="complex",
            display_name="Complex Tool",
            description="Requires special setup",
            category=ModuleCategory.TOOLS,
        )

    def check_available(self) -> bool:
        # Custom availability check
        return some_dependency_exists()

    def install(self, config_path: Path) -> InstallResult:
        # Step 1: Download
        result = run(["curl", "-fsSL", "https://example.com/install.sh"])
        if not result.success:
            return InstallResult(False, f"Download failed: {result.stderr}")

        # Step 2: Run installer
        result = run(["bash", "-c", result.stdout])
        if not result.success:
            return InstallResult(False, f"Install failed: {result.stderr}")

        # Step 3: Write config
        self._add_config(config_path)

        return InstallResult(True, "Complex tool installed")

    def uninstall(self, config_path: Path) -> InstallResult:
        self._remove_config(config_path)
        return InstallResult(True, "Complex tool removed")
```

---

## Working Agreements

### Before Making Changes

1. **Read existing code first** — Understand the patterns already in use
2. **Run tests** — Ensure baseline passes: `uv run pytest tests/ -v`
3. **Check types** — Run `uv run mypy src/` before and after changes

### When Adding Features

1. **Follow existing patterns** — Use `ConfigOnlyModule` or `GitCloneModule` when possible
2. **Add to registry** — Update `modules/__init__.py` with new modules
3. **Write tests** — Minimum: test `info`, `get_config_content`, `install`
4. **Update docs** — Add to README if user-facing

### When Fixing Bugs

1. **Write a failing test first** — Reproduce the bug in a test
2. **Fix minimally** — Change only what's necessary
3. **Verify fix** — Run the specific test and full suite

### What NOT to Do

- **Don't add multi-shell support** — ZSH only, this is intentional
- **Don't use `subprocess` directly** — Use `utils/process.py` wrappers
- **Don't write to files directly** — Use `utils/files.py` for backup support
- **Don't catch broad exceptions** — Be specific about what can fail
- **Don't add optional dependencies** — Keep the binary small
- **Don't modify `pyproject.toml` dependencies** without discussion

---

## Build & Release

### Building the Binary

```bash
# Containerized build (recommended for release)
# Uses Debian 11 (glibc 2.31) for RHEL 9+/Ubuntu 24.04+ compatibility
python scripts/build.py

# Local build (for development testing)
python scripts/build.py --local

# Verify binary
./dist/myshell --version
./dist/myshell list
```

### Release Workflow

```bash
VERSION="2.1.0"

# 1. Update version
sed -i "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" \
  src/myshell_rfd/__init__.py

# 2. Run full checks
uv run pytest tests/ -v
uv run ruff check src/ tests/
uv run mypy src/

# 3. Commit and tag
git add -A
git commit -m "Release v$VERSION"
git tag "v$VERSION"
git push origin main --tags

# 4. Build and release
python scripts/build.py
gh release create "v$VERSION" \
  --title "MyShell_RFD v$VERSION" \
  --generate-notes \
  dist/myshell#myshell_rfd-v$VERSION
```

---

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| Tests fail with permission error | Run with `--all` permissions or check sandbox |
| Import errors | Run `uv pip install -e ".[dev]"` |
| mypy errors about missing stubs | Add to `[tool.mypy]` ignore list if third-party |
| Binary too large | Check for unnecessary `--collect-data` in build.py |
| Config not loading | Check `~/.myshell_rfd/config.toml` syntax |

### Debug Commands

```bash
# Verbose test output
uv run pytest tests/ -v -s --tb=long

# Type check with verbose errors
uv run mypy src/ --show-error-codes --pretty

# Check what ruff would fix
uv run ruff check src/ --diff

# Run single module manually
uv run python -c "from myshell_rfd.modules.aws import AWSModule; print(AWSModule().info)"
```

---

## File Locations Reference

| Purpose | Path |
|---------|------|
| User config | `~/.myshell_rfd/config.toml` |
| Profiles | `~/.myshell_rfd/profiles/*.toml` |
| ZSH config (generated) | `~/.myshell_rfd/config.zsh` |
| Rollback snapshots | `~/.myshell_rfd/backups/` |
| Offline cache | `~/.myshell_rfd/cache/` |
| External plugins | `~/.myshell_rfd/plugins/` |
| Package version | `src/myshell_rfd/__init__.py` |
| Dependencies | `pyproject.toml` |
| Build script | `scripts/build.py` |
