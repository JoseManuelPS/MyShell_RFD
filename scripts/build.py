#!/usr/bin/env python3
"""Build script for MyShell_RFD.

Creates a portable binary executable using Docker/Podman for glibc compatibility.
The binary is built on Debian 11 (glibc 2.31) for compatibility with:
- RHEL 9+ (glibc 2.34)
- Ubuntu 24.04+ (glibc 2.39)
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"

# Container image name
IMAGE_NAME = "myshell-rfd-builder"

# Dockerfile content (Debian 11 Bullseye with glibc 2.31)
# Compatible with: RHEL 9+ (glibc 2.34), Ubuntu 24.04+ (glibc 2.39)
DOCKERFILE_CONTENT = """\
FROM python:3.12-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \\
    binutils git \\
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash builder
USER builder
WORKDIR /home/builder

RUN pip install --user uv
ENV PATH="/home/builder/.local/bin:${PATH}"

WORKDIR /build
COPY --chown=builder:builder . .

# Install only runtime dependencies + PyInstaller (no dev dependencies)
RUN uv pip install --system \\
    textual rich typer \\
    tomli-w httpx platformdirs \\
    pyinstaller

# Install the package without dependencies (already installed above)
RUN uv pip install --system --no-deps -e .

RUN python scripts/build.py --local --no-verify

CMD ["cat", "/build/dist/myshell"]
"""


def find_container_runtime() -> str | None:
    """Find available container runtime (podman or docker)."""
    for runtime in ["podman", "docker"]:
        if shutil.which(runtime):
            return runtime
    return None


def clean() -> None:
    """Clean previous build artifacts."""
    for directory in [DIST_DIR, BUILD_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"Cleaned {directory}")


def build_local(*, debug: bool = False) -> Path:
    """Build the executable locally (without container)."""
    sep = ";" if sys.platform == "win32" else ":"

    args = [
        sys.executable, "-m", "PyInstaller",
        str(SRC_DIR / "myshell_rfd" / "__main__.py"),
        "--name=myshell", "--clean", "--noconfirm", "--onefile",
        f"--add-data={SRC_DIR / 'myshell_rfd' / 'assets'}{sep}myshell_rfd/assets",
        # Application modules
        "--hidden-import=myshell_rfd.modules",
        "--hidden-import=myshell_rfd.modules.aws",
        "--hidden-import=myshell_rfd.modules.containers",
        "--hidden-import=myshell_rfd.modules.kubernetes",
        "--hidden-import=myshell_rfd.modules.cloud",
        "--hidden-import=myshell_rfd.modules.tools",
        "--hidden-import=myshell_rfd.modules.vcs",
        "--hidden-import=myshell_rfd.modules.shell_plugins",
        "--hidden-import=myshell_rfd.modules.themes",
        "--hidden-import=myshell_rfd.cli",
        "--hidden-import=myshell_rfd.cli.commands",
        "--hidden-import=myshell_rfd.cli.install",
        "--hidden-import=myshell_rfd.cli.profile",
        "--hidden-import=myshell_rfd.cli.rollback",
        "--hidden-import=myshell_rfd.tui",
        "--hidden-import=myshell_rfd.tui.app",
        "--hidden-import=myshell_rfd.tui.screens",
        "--hidden-import=myshell_rfd.tui.widgets",
        "--hidden-import=myshell_rfd.plugins",
        # Third-party dependencies
        "--hidden-import=textual",
        "--hidden-import=textual.app",
        "--hidden-import=textual.widgets",
        "--hidden-import=rich",
        "--hidden-import=rich.console",
        "--hidden-import=typer",
        "--hidden-import=tomli_w",
        # Exclude tomli (uses mypyc which causes binary issues)
        "--exclude-module=tomli",
        "--hidden-import=httpx",
        "--collect-data=textual",
        "--collect-data=rich",
        "--collect-submodules=rich",
        # Exclude development tools
        "--exclude-module=pytest",
        "--exclude-module=_pytest",
        "--exclude-module=ruff",
        # Exclude unnecessary extras
        "--exclude-module=IPython",
        "--exclude-module=setuptools",
        "--exclude-module=pip",
    ]

    if not debug:
        args.extend(["--strip", "--optimize=2"])
    else:
        args.append("--debug=all")

    print("Building MyShell_RFD locally...")
    result = subprocess.run(args, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)

    exe_path = DIST_DIR / "myshell"
    print(f"\nBuild complete: {exe_path}")

    if exe_path.exists():
        print(f"Size: {exe_path.stat().st_size / 1024 / 1024:.2f} MB")

    return exe_path


def build_container(runtime: str, *, debug: bool = False) -> Path:
    """Build the executable using Docker/Podman container."""
    print(f"Building MyShell_RFD using {runtime}...")
    print("Using Debian 11 (glibc 2.31) for RHEL 9+ / Ubuntu 24.04+ compatibility\n")

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # Create temporary Dockerfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".Dockerfile", delete=False) as f:
        f.write(DOCKERFILE_CONTENT)
        dockerfile_path = f.name

    try:
        # Build container image
        print("[1/3] Building container image...")
        build_cmd = [
            runtime, "build",
            "-t", IMAGE_NAME,
            "-f", dockerfile_path,
            str(PROJECT_ROOT),
        ]

        result = subprocess.run(build_cmd)
        if result.returncode != 0:
            print("Container build failed!")
            sys.exit(1)

        # Extract binary from container
        print("\n[2/3] Extracting binary...")
        container_name = f"{IMAGE_NAME}-extract"

        subprocess.run([runtime, "rm", "-f", container_name], capture_output=True)

        result = subprocess.run(
            [runtime, "create", "--name", container_name, IMAGE_NAME],
            capture_output=True,
        )
        if result.returncode != 0:
            print(f"Failed to create container: {result.stderr.decode()}")
            sys.exit(1)

        result = subprocess.run([
            runtime, "cp",
            f"{container_name}:/build/dist/myshell",
            str(DIST_DIR / "myshell"),
        ])
        if result.returncode != 0:
            print("Failed to copy binary from container!")
            sys.exit(1)

        subprocess.run([runtime, "rm", "-f", container_name], capture_output=True)

        exe_path = DIST_DIR / "myshell"
        if exe_path.exists():
            exe_path.chmod(0o755)

        print("\n[3/3] Build complete!")
        print(f"Binary: {exe_path}")

        if exe_path.exists():
            print(f"Size: {exe_path.stat().st_size / 1024 / 1024:.2f} MB")

        return exe_path

    finally:
        Path(dockerfile_path).unlink(missing_ok=True)


def verify(exe_path: Path) -> bool:
    """Verify the built executable."""
    print("\nVerifying build...")

    if not exe_path.exists():
        print(f"Binary not found: {exe_path}")
        return False

    for cmd, name in [
        ([str(exe_path), "--version"], "Version"),
        ([str(exe_path), "--help"], "Help"),
        ([str(exe_path), "list"], "List"),
    ]:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"{name} check failed: {result.stderr}")
            return False
        if name == "Version":
            print(f"{name}: {result.stdout.strip()}")
        else:
            print(f"{name}: OK")

    print("\nVerification passed!")
    return True


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build MyShell_RFD executable",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/build.py              # Build using container (recommended)
  python scripts/build.py --local      # Build locally (current system glibc)
  python scripts/build.py --clean      # Clean build artifacts only
        """,
    )
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts only")
    parser.add_argument("--local", action="store_true", help="Build locally (less portable)")
    parser.add_argument("--debug", action="store_true", help="Enable debug build")
    parser.add_argument("--no-verify", action="store_true", help="Skip verification")
    parser.add_argument("--runtime", choices=["docker", "podman"], help="Force container runtime")

    args = parser.parse_args()

    if args.clean:
        clean()
        return

    clean()

    if args.local:
        exe_path = build_local(debug=args.debug)
    else:
        runtime = args.runtime or find_container_runtime()
        if not runtime:
            print("ERROR: No container runtime found (docker or podman)")
            print("Install docker or podman, or use --local for local build")
            sys.exit(1)
        exe_path = build_container(runtime, debug=args.debug)

    if not args.no_verify and exe_path.exists():
        if not verify(exe_path):
            sys.exit(1)

    print("\nDone!")


if __name__ == "__main__":
    main()
