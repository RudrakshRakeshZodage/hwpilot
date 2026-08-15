"""Virtual environment creation routines."""

import sys
import os
import venv
from pathlib import Path
from typing import Tuple
from hwpilot.utils.subprocess_utils import run_cmd


def get_venv_python(env_path: Path) -> Path:
    """Returns absolute path to python executable inside virtual environment."""
    if sys.platform == "win32":
        return env_path / "Scripts" / "python.exe"
    return env_path / "bin" / "python"


def create_environment(env_path_str: str, use_uv: bool = True) -> Tuple[bool, str, Path]:
    """
    Creates an isolated virtual environment at the target path using venv or uv.
    Returns (success, message, python_executable_path).
    """
    env_path = Path(env_path_str).resolve()
    python_exe = get_venv_python(env_path)

    # 1. If environment already exists and has python executable, reuse
    if python_exe.exists():
        return True, f"Using existing virtual environment at {env_path}", python_exe

    env_path.mkdir(parents=True, exist_ok=True)

    # 2. Try fast creation with `uv` if available
    if use_uv:
        code, stdout, stderr = run_cmd(["uv", "venv", str(env_path)])
        if code == 0 and python_exe.exists():
            return True, f"Created virtual environment using uv at {env_path}", python_exe

    # 3. Fallback to standard Python `venv` module
    try:
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(env_path)
        if python_exe.exists():
            return True, f"Created virtual environment using standard venv at {env_path}", python_exe
        else:
            return False, f"venv completed but Python binary missing at {python_exe}", python_exe
    except Exception as e:
        return False, f"Failed to create virtual environment: {str(e)}", python_exe
