# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MyShell_RFD is a modular ZSH/Bash configuration tool that builds into a single self-contained shell script. It installs shell tooling (completions, aliases, plugins) for common DevOps tools by writing to `~/.myshell_rfd/config`, which is sourced from `.zshrc`.

## Commands

```bash
make build        # Compile src/ into dist/myshell_rfd-<VERSION>
make test         # Build then run all BATS tests
make test-deps    # Clone bats-core into tests/libs/bats (auto-run by make test)
make clean        # Remove dist/
make install      # Build and install to /usr/local/bin (requires sudo)
```

Run a single test file:
```bash
./tests/libs/bats/bin/bats tests/core/core.bats
./tests/libs/bats/bin/bats tests/modules/iac.bats
```

The version is defined in `Makefile` (`VERSION := vX.Y.Z`). The build output is `dist/myshell_rfd-<VERSION>`.

## Architecture

### Build Pipeline

`build.sh` concatenates source files in this order into a single executable:

1. **Header** — version variable and banner comment
2. **Assets** — `src/assets/p10k.zsh` embedded as base64 (`P10K_ZSH_CONTENT_BASE64`)
3. **Core** — all `src/core/*.sh` files (alphabetical order)
4. **Modules** — all `src/modules/*.sh` files (alphabetical order)
5. **Entry point** — `src/main.sh`

The built artifact is what gets distributed and installed, not the source files directly.

### Module Registration Pattern

Every module file registers itself into a global associative array:

```bash
MODULES["ModuleName"]="function_name"
```

`main.sh` reads this registry to run modules interactively or by name. When adding a new module, register it this way — no other wiring needed.

### Core Utilities (`src/core/`)

| File | Purpose |
|------|---------|
| `colors.sh` | ANSI color/style variables (`RED`, `BOLD`, etc.) |
| `lecho.sh` | Logging (`lecho "INFO\|SUCCESS\|WARN\|ERROR\|DEBUG" "msg"`) |
| `ui.sh` | `print_header`, `prompt_yes_no`, SIGINT trap |
| `utils.sh` | Config file management (`init_config`, `add_to_config`, `backup_file`, `ensure_zshrc_source`, `enable_omz_plugin`), `check_binary` |
| `bootstrap.sh` | Checks/installs curl, git, zsh, Oh My Zsh |
| `update.sh` | Self-update via GitHub Releases API |

### Config Writing Convention

Modules write to `~/.myshell_rfd/config` using `add_to_config`:

```bash
add_to_config "SectionName" "$config_content"
```

`add_to_config` is idempotent — it skips the write if a section header `## SectionName` already exists. Modules guard themselves with `check_binary <tool>` before prompting.

### Tests (`tests/`)

Tests are BATS files split into `tests/core/` and `tests/modules/`. The shared `tests/test_helper.bash` provides `common_setup`/`common_teardown` and a `mock_command` helper that creates executable stubs under `$BATS_TMPDIR/mock_bin/` and prepends that directory to `$PATH`.

Note: `tests/core/core.bats` hardcodes the version in the artifact path — update it when bumping `VERSION` in the Makefile.

### `AUTO_YES` Mode

The global `AUTO_YES=true` flag (set by `myshell_rfd a` or `myshell_rfd all`) causes all `prompt_yes_no` calls to auto-accept using the default value. Modules that have side effects requiring user confirmation (like `chsh`) must check this flag explicitly.
