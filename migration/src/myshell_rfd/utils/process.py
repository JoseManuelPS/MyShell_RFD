"""Process execution utility for MyShell_RFD.

Provides safe subprocess execution with output capture and streaming.
"""

import asyncio
import os
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Any

from myshell_rfd.utils.logger import get_logger


@dataclass
class ProcessResult:
    """Result of a process execution.

    Attributes:
        returncode: The process return code.
        stdout: Standard output as string.
        stderr: Standard error as string.
        command: The executed command.
    """

    returncode: int
    stdout: str = ""
    stderr: str = ""
    command: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Check if the process succeeded."""
        return self.returncode == 0

    @property
    def output(self) -> str:
        """Get combined stdout and stderr."""
        parts = []
        if self.stdout:
            parts.append(self.stdout)
        if self.stderr:
            parts.append(self.stderr)
        return "\n".join(parts)


class ProcessRunner:
    """Safe process execution with logging and error handling.

    Wraps subprocess calls with consistent error handling,
    output capture, and optional streaming.
    """

    def __init__(
        self,
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout: float | None = 300.0,
    ) -> None:
        """Initialize the process runner.

        Args:
            cwd: Default working directory for commands.
            env: Environment variables to add/override.
            timeout: Default timeout in seconds.
        """
        self._cwd = cwd
        self._env = dict(os.environ)
        if env:
            self._env.update(env)
        self._timeout = timeout
        self._logger = get_logger()

    def _build_env(self, extra_env: Mapping[str, str] | None = None) -> dict[str, str]:
        """Build environment dict with optional extras."""
        env = self._env.copy()
        if extra_env:
            env.update(extra_env)
        return env

    def run(
        self,
        command: Sequence[str] | str,
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout: float | None = None,
        capture: bool = True,
        check: bool = False,
        shell: bool = False,
        stdin: str | None = None,
    ) -> ProcessResult:
        """Run a command synchronously.

        Args:
            command: Command as string or list of arguments.
            cwd: Working directory (overrides default).
            env: Additional environment variables.
            timeout: Command timeout (overrides default).
            capture: Capture stdout/stderr.
            check: Raise exception on non-zero exit.
            shell: Run through shell.
            stdin: Input to send to process stdin.

        Returns:
            ProcessResult with output and return code.

        Raises:
            subprocess.CalledProcessError: If check=True and command fails.
            subprocess.TimeoutExpired: If command times out.
        """
        if isinstance(command, str):
            cmd_list = command.split() if not shell else [command]
        else:
            cmd_list = list(command)

        self._logger.debug(f"Running: {' '.join(cmd_list)}")

        try:
            result = subprocess.run(
                cmd_list if not shell else cmd_list[0] if len(cmd_list) == 1 else " ".join(cmd_list),
                cwd=cwd or self._cwd,
                env=self._build_env(env),
                timeout=timeout or self._timeout,
                capture_output=capture,
                text=True,
                check=check,
                shell=shell,
                input=stdin,
            )

            return ProcessResult(
                returncode=result.returncode,
                stdout=result.stdout or "",
                stderr=result.stderr or "",
                command=cmd_list,
            )

        except subprocess.CalledProcessError as e:
            self._logger.error(f"Command failed: {e}")
            raise

        except subprocess.TimeoutExpired as e:
            self._logger.error(f"Command timed out after {e.timeout}s")
            raise

    def run_stream(
        self,
        command: Sequence[str] | str,
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        stdout_handler: IO[str] | None = None,
        stderr_handler: IO[str] | None = None,
        shell: bool = False,
    ) -> ProcessResult:
        """Run a command with streaming output.

        Args:
            command: Command as string or list of arguments.
            cwd: Working directory.
            env: Additional environment variables.
            stdout_handler: File-like object for stdout streaming.
            stderr_handler: File-like object for stderr streaming.
            shell: Run through shell.

        Returns:
            ProcessResult with return code (stdout/stderr may be empty if streamed).
        """
        if isinstance(command, str):
            cmd_list = command.split() if not shell else [command]
        else:
            cmd_list = list(command)

        self._logger.debug(f"Running (stream): {' '.join(cmd_list)}")

        stdout_lines: list[str] = []
        stderr_lines: list[str] = []

        with subprocess.Popen(
            cmd_list if not shell else " ".join(cmd_list),
            cwd=cwd or self._cwd,
            env=self._build_env(env),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=shell,
        ) as proc:
            # Read stdout
            if proc.stdout:
                for line in proc.stdout:
                    stdout_lines.append(line)
                    if stdout_handler:
                        stdout_handler.write(line)

            # Read stderr
            if proc.stderr:
                for line in proc.stderr:
                    stderr_lines.append(line)
                    if stderr_handler:
                        stderr_handler.write(line)

            proc.wait()

            return ProcessResult(
                returncode=proc.returncode or 0,
                stdout="".join(stdout_lines),
                stderr="".join(stderr_lines),
                command=cmd_list,
            )

    async def run_async(
        self,
        command: Sequence[str] | str,
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout: float | None = None,
        stdin: str | None = None,
    ) -> ProcessResult:
        """Run a command asynchronously.

        Args:
            command: Command as string or list of arguments.
            cwd: Working directory.
            env: Additional environment variables.
            timeout: Command timeout.
            stdin: Input to send to process stdin.

        Returns:
            ProcessResult with output and return code.
        """
        if isinstance(command, str):
            cmd_list = command.split()
        else:
            cmd_list = list(command)

        self._logger.debug(f"Running (async): {' '.join(cmd_list)}")

        proc = await asyncio.create_subprocess_exec(
            *cmd_list,
            cwd=cwd or self._cwd,
            env=self._build_env(env),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE if stdin else None,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(stdin.encode() if stdin else None),
                timeout=timeout or self._timeout,
            )

            return ProcessResult(
                returncode=proc.returncode or 0,
                stdout=stdout.decode() if stdout else "",
                stderr=stderr.decode() if stderr else "",
                command=cmd_list,
            )

        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            self._logger.error(f"Async command timed out")
            raise

    def which(self, name: str) -> Path | None:
        """Find the path of an executable.

        Args:
            name: The executable name.

        Returns:
            The path to the executable, or None if not found.
        """
        path = shutil.which(name, path=self._env.get("PATH"))
        return Path(path) if path else None

    def git_clone(
        self,
        url: str,
        dest: Path,
        *,
        depth: int | None = 1,
        branch: str | None = None,
    ) -> ProcessResult:
        """Clone a git repository.

        Args:
            url: The repository URL.
            dest: Destination directory.
            depth: Clone depth (None for full clone).
            branch: Specific branch to clone.

        Returns:
            ProcessResult from the git clone command.
        """
        cmd: list[str] = ["git", "clone"]

        if depth is not None:
            cmd.extend(["--depth", str(depth)])

        if branch:
            cmd.extend(["--branch", branch])

        cmd.extend([url, str(dest)])

        return self.run(cmd)

    def download(
        self,
        url: str,
        dest: Path,
        *,
        executable: bool = False,
    ) -> ProcessResult:
        """Download a file using curl.

        Args:
            url: The URL to download.
            dest: Destination file path.
            executable: Make the file executable after download.

        Returns:
            ProcessResult from the curl command.
        """
        dest.parent.mkdir(parents=True, exist_ok=True)

        result = self.run(
            ["curl", "-fsSL", "-o", str(dest), url],
            timeout=600.0,  # Allow longer timeout for downloads
        )

        if result.success and executable:
            dest.chmod(dest.stat().st_mode | 0o111)

        return result


# Default instance
_runner: ProcessRunner | None = None


def get_runner() -> ProcessRunner:
    """Get the default ProcessRunner instance."""
    global _runner
    if _runner is None:
        _runner = ProcessRunner()
    return _runner
