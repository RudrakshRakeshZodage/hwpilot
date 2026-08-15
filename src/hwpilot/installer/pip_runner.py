"""Package installer routines using pip/uv."""

from pathlib import Path
from typing import List, Tuple
from hwpilot.models.plan import InstallationPlan
from hwpilot.utils.subprocess_utils import run_cmd
from hwpilot.utils.logger import get_logger

logger = get_logger()


def install_plan(plan: InstallationPlan, python_exe: Path) -> Tuple[bool, str, List[str]]:
    """
    Installs packages defined in InstallationPlan inside the specified virtual environment.
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
    cmd = py_cmd + ["-m", "pip", "install"]

    if plan.index_url:
        cmd.extend(["--index-url", plan.index_url, "--extra-index-url", "https://pypi.org/simple"])

    for pkg in plan.packages:
        if pkg.version:
            cmd.append(f"{pkg.name}=={pkg.version}")
        else:
            cmd.append(pkg.name)

    logger.info(f"Executing installation command: {' '.join(cmd)}")
    logs.append(f"Command: {' '.join(cmd)}")

    code, stdout, stderr = run_cmd(cmd, timeout=600)  # ML package downloads can take a few minutes
    logs.append(f"Install stdout:\n{stdout}")
    logs.append(f"Install stderr:\n{stderr}")

    if code == 0:
        return True, "All resolved packages installed successfully.", logs
    else:
        return False, f"Package installation failed with exit code {code}.\nStderr: {stderr}", logs
