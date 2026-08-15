"""Package installer routines using pip with real-time download streaming and unpacking progress."""

from pathlib import Path
from typing import List, Tuple
from hwpilot.models.plan import InstallationPlan
from hwpilot.utils.subprocess_utils import run_cmd, run_cmd_stream
from hwpilot.utils.logger import get_logger

logger = get_logger()


def format_pip_line(line: str):
    """Formats pip stream output with clear visual feedback for downloading and unpacking."""
    if "Installing collected packages:" in line:
        print(f"\n  📦 {line}", flush=True)
        print("  ⏳ Unpacking and writing CUDA runtime binaries (~2.5 GB) to disk... Please wait a moment.\n", flush=True)
    elif "Successfully installed" in line:
        print(f"\n  ✅ {line}\n", flush=True)
    elif "Collecting" in line:
        print(f"  📦 {line}", flush=True)
    elif "Using cached" in line or "Downloading" in line:
        print(f"  ⬇️  {line}", flush=True)
    else:
        print(f"  {line}", flush=True)


def install_plan(plan: InstallationPlan, python_exe: Path, stream_output: bool = True) -> Tuple[bool, str, List[str]]:
    """
    Installs packages defined in InstallationPlan inside the specified virtual environment.
    Streams download and installation progress (e.g. 2.4 GB PyTorch wheels) in real-time.
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
        print("\n📥 Downloading & installing ML packages (PyTorch / CUDA wheels ~2.4GB)...")
        code, lines = run_cmd_stream(cmd, line_callback=format_pip_line)
        logs.extend(lines)
    else:
        code, stdout, stderr = run_cmd(cmd, timeout=900)
        logs.append(f"Install stdout:\n{stdout}\nstderr:\n{stderr}")

    if code == 0:
        return True, "All resolved packages installed successfully.", logs
    else:
        return False, f"Package installation failed with exit code {code}.", logs
