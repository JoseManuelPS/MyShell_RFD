# Contributing Guide

Practical guide for developing and maintaining MyShell_RFD.

## Environment Setup

```bash
cd migration

# Create environment with uv
uv venv
source .venv/bin/activate

# Install dependencies (including dev)
uv pip install -e ".[dev]"
```

## Development Workflow

```bash
# 1. Verify initial state
uv run pytest tests/ -v

# 2. Make changes...

# 3. Quality checks
uv run ruff check src/ tests/
uv run ruff format src/ tests/
uv run mypy src/

# 4. Run tests
uv run pytest tests/ -v

# 5. Manual testing
uv run myshell --help
uv run myshell list
```

## Adding a New Module

1. Create file in `src/myshell_rfd/modules/`
2. Inherit from `BaseModule`, `ConfigOnlyModule`, or `GitCloneModule`
3. Register in `src/myshell_rfd/modules/__init__.py`
4. Add tests in `tests/test_modules/`

```python
# src/myshell_rfd/modules/example.py
from myshell_rfd.core.module_base import (
    ConfigOnlyModule,
    ModuleInfo,
    ModuleCategory,
)


class ExampleModule(ConfigOnlyModule):
    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="example",
            display_name="Example Tool",
            description="Example module",
            category=ModuleCategory.TOOLS,
            binary="example",
        )

    def get_config_content(self) -> str:
        return '''
# Example aliases
alias ex="example"
'''
```

## Build

```bash
# Portable build (Docker/Podman - recommended)
python scripts/build.py

# Local build (less portable)
python scripts/build.py --local

# Binary output: migration/dist/myshell
```

## Releases

### Versioning

We use [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., `2.0.0`, `2.1.0`, `2.1.1`)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Workflow

```bash
# 1. Ensure clean state
git status
uv run pytest tests/ -v
uv run ruff check src/ tests/
uv run mypy src/

# 2. Update version in src/myshell_rfd/__init__.py
# __version__ = "2.1.0"

# 3. Commit and tag
git add -A
git commit -m "Release v2.1.0"
git tag v2.1.0

# 4. Push
git push origin main --tags

# 5. Build binary
python scripts/build.py

# 6. Create GitHub release
gh release create v2.1.0 \
  --title "MyShell_RFD v2.1.0" \
  --notes "## Changes
- Feature X
- Fix Y
- Improvement Z" \
  dist/myshell#myshell_rfd-v2.1.0
```

### Quick Release Example

```bash
VERSION="2.1.0"

# Update version
sed -i "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" \
  src/myshell_rfd/__init__.py

# Commit, tag, push
git add -A
git commit -m "Release v$VERSION"
git tag "v$VERSION"
git push origin main --tags

# Build and release
python scripts/build.py
gh release create "v$VERSION" \
  --title "MyShell_RFD v$VERSION" \
  --generate-notes \
  dist/myshell#myshell_rfd-v$VERSION
```

The binary will be uploaded as `myshell_rfd-v2.1.0` (no extension).

## Commit Messages

```
<type>: <short description>

[optional body]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring (no functional change)
- `test`: Add or modify tests
- `chore`: Maintenance tasks

Examples:
```
feat: add terraform module
fix: resolve config loading on first run
docs: update installation instructions
refactor: simplify module registry
test: add tests for rollback manager
chore: update dependencies
```

## Pre-Release Checklist

- [ ] Tests pass: `uv run pytest tests/ -v`
- [ ] No lint errors: `uv run ruff check src/ tests/`
- [ ] No type errors: `uv run mypy src/`
- [ ] Version updated in `__init__.py`
- [ ] Build successful: `python scripts/build.py`
- [ ] Binary verified: `./dist/myshell --version`
