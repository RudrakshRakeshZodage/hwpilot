"""Package installer routines using pip with interactive Rich progress bars and live ETA/speed."""

import re
from pathlib import Path
from typing import List, Tuple, Optional
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
)
from rich.console import Console
from hwpilot.models.plan import InstallationPlan
from hwpilot.utils.subprocess_utils import run_cmd, run_cmd_stream
from hwpilot.utils.logger import get_logger

logger = get_logger()
console = Console()

PROGRESS_REGEX = re.compile(
    r"([\d\.]+)\s*/\s*([\d\.]+)\s*(kB|MB|GB)\s+([\d\.]+)\s*(kB/s|MB/s|GB/s)\s*(?:eta\s+)?([\d:]+)",
    re.IGNORECASE,
)

DOWNLOAD_HEADER_REGEX = re.compile(
    r"Downloading\s+([^\s]+)\s*\(([\d\.]+)\s*(kB|MB|GB)\)",
    re.IGNORECASE,
)

UNIT_MULTIPLIERS = {
    "kb": 1024,
    "mb": 1024 * 1024,
    "gb": 1024 * 1024 * 1024,
}


class PipInteractiveProgress:
    """Manages an interactive Rich progress bar driven by pip subprocess output."""

    def __init__(self, progress: Progress):
        self.progress = progress
        self.download_task: Optional[int] = None
        self.unpack_task: Optional[int] = None
        self.current_pkg: str = "PyTorch Packages"

    def handle_line(self, line: str):
        # 1. New package collecting / downloading
        if "Collecting" in line:
            pkg_name = line.replace("Collecting", "").strip().split()[0]
            self.current_pkg = pkg_name

        download_match = DOWNLOAD_HEADER_REGEX.search(line)
        if download_match:
            filename = download_match.group(1)
            size = float(download_match.group(2))
            unit = download_match.group(3).lower()
            total_bytes = size * UNIT_MULTIPLIERS.get(unit, 1024 * 1024)

            short_name = filename.split("-")[0] if "-" in filename else filename
            desc = f"[bold cyan]Downloading {short_name}[/bold cyan]"

            if self.download_task is None:
                self.download_task = self.progress.add_task(
                    desc,
                    total=total_bytes,
                    completed=0,
                )
            else:
                self.progress.update(
                    self.download_task,
                    description=desc,
                    total=total_bytes,
                    completed=0,
                )

        # 2. Live progress bar line (bytes / speed / ETA)
        prog_match = PROGRESS_REGEX.search(line)
        if prog_match:
            current_val = float(prog_match.group(1))
            total_val = float(prog_match.group(2))
            unit = prog_match.group(3).lower()
            multiplier = UNIT_MULTIPLIERS.get(unit, 1024 * 1024)

            completed_bytes = current_val * multiplier
            total_bytes = total_val * multiplier

            if self.download_task is None:
                self.download_task = self.progress.add_task(
                    f"[bold cyan]Downloading {self.current_pkg}[/bold cyan]",
                    total=total_bytes,
                    completed=completed_bytes,
                )
            else:
                self.progress.update(
                    self.download_task,
                    completed=completed_bytes,
                    total=total_bytes,
                )

        # 3. Package Unpacking & Installing
        if "Installing collected packages:" in line:
            if self.download_task is not None:
                self.progress.update(self.download_task, visible=False)
            if self.unpack_task is None:
                self.unpack_task = self.progress.add_task(
                    "[bold yellow]📦 Unpacking and writing CUDA runtime binaries to disk (~2.5 GB)...[/bold yellow]",
                    total=None,
                )

        # 4. Successfully installed
        if "Successfully installed" in line:
            if self.unpack_task is not None:
                self.progress.update(
                    self.unpack_task,
                    description="[bold green]✓ Unpacking and installation complete[/bold green]",
                    completed=1,
                    total=1,
                )


def install_plan(plan: InstallationPlan, python_exe: Path, stream_output: bool = True) -> Tuple[bool, str, List[str]]:
    """
    Installs packages defined in InstallationPlan inside the specified virtual environment.
    Streams download and installation progress (e.g. 2.4 GB PyTorch wheels) with interactive Rich progress bars.
    Returns (success, status_summary, log_entries).
    """
    if not python_exe.exists() and not plan.is_global:
        return False, f"Python executable not found at {python_exe}", []

    logs: List[str] = []
    py_cmd = [str(python_exe)] if not plan.is_global else ["python"]

    # 1. Upgrade pip, setuptools, wheel first
    upgrade_cmd = py_cmd + ["-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"]
    code, stdout, stderr = run_cmd(upgrade_cmd, timeout=120)
    logs.append(f"Pip upgrade output:\n{stdout}\n{stderr}")

    # 2. Build install command for resolved packages
    cmd = py_cmd + ["-m", "pip", "install", "--progress-bar", "on"]

    if plan.index_url:
        cmd.extend(["--index-url", plan.index_url, "--extra-index-url", "https://pypi.org/simple"])

    for pkg in plan.packages:
        if pkg.version:
            cmd.append(f"{pkg.name}=={pkg.version}")
        else:
            cmd.append(pkg.name)

    logger.info(f"Executing installation command: {' '.join(cmd)}")
    logs.append(f"Command: {' '.join(cmd)}")

    if stream_output:
        console.print("\n[bold cyan]📥 Downloading & Installing ML Packages (PyTorch / CUDA ~2.5GB)...[/bold cyan]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}[/bold cyan]"),
            BarColumn(bar_width=25),
            TextColumn("[bold green]{task.percentage:>3.0f}%[/bold green]"),
            DownloadColumn(),
            TransferSpeedColumn(),
            TextColumn("[yellow]ETA:[/yellow]"),
            TimeRemainingColumn(),
            TextColumn("[dim]Elapsed:[/dim]"),
            TimeElapsedColumn(),
            console=console,
            transient=False,
        ) as progress:
            pip_tracker = PipInteractiveProgress(progress)
            code, lines = run_cmd_stream(cmd, line_callback=pip_tracker.handle_line)
            logs.extend(lines)
    else:
        code, stdout, stderr = run_cmd(cmd, timeout=900)
        logs.append(f"Install stdout:\n{stdout}\nstderr:\n{stderr}")

    if code == 0:
        return True, "All resolved packages installed successfully.", logs
    else:
        return False, f"Package installation failed with exit code {code}.", logs
