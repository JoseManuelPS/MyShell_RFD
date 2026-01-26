# MyShell_RFD

![Version](https://img.shields.io/badge/version-v1.0.0-blue.svg)
![Build](https://img.shields.io/badge/build-passing-green.svg)

**MyShell_RFD** is a professional, modular configuration tool for ZSH and Bash environments.

## Features

- **Modular Architecture**: separate core logic from feature modules.
- **Single Binary Distribution**: Builds into a single self-contained script.
- **CLI Management**: Install specific modules, clean configuration, and self-update.

## Installation

### Via MyEnv_RFD (Recommended)
Add `myshell_rfd` to your `myenv_rfd` configuration and deploy.

### Manual
```bash
make install
```

## Usage

### Interactive Mode
Run without arguments to start the full interactive configuration wizard:
```bash
myshell_rfd
```

### CLI Commands

#### Install Specific Module
Run a specific module (e.g., AWS, Kubectl) directly:
```bash
myshell_rfd install AWS
myshell_rfd install Kubectl
```

#### Selective Install
Launch an interactive menu to choose a module:
```bash
myshell_rfd install
```

#### Update
Update the tool to the latest version available on GitHub:
```bash
myshell_rfd update
```
*Note: Requires sudo permissions to overwrite `/usr/local/bin`.*

#### Clean / Reset
Remove the current configuration and back it up:
```bash
myshell_rfd clean
```
*Backups are stored in `~/.myshell_rfd/backups`.*

## Configuration
- **Root**: `~/.myshell_rfd/`
- **Config**: `~/.myshell_rfd/config`
- **Backups**: `~/.myshell_rfd/backups/`

## Development
- `make build`: Generate `dist/myshell_rfd`.
- `make test`: Run BATS tests.

## License
Confidential / Proprietary.