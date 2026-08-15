"""Virtual environment creation routines with automatic pip verification."""

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


def ensure_pip_installed(python_exe: Path) -> bool:
    """Checks if pip is available in the virtual environment, installs if missing."""
    code, _, _ = run_cmd([str(python_exe), "-m", "pip", "--version"])
    if code == 0:
        return True
    
    # Pip is missing (e.g., from unseeded uv venv). Install via ensurepip.
    code_ensure, _, _ = run_cmd([str(python_exe), "-m", "ensurepip", "--upgrade"])
    return code_ensure == 0


def create_environment(env_path_str: str, use_uv: bool = True) -> Tuple[bool, str, Path]:
    """
    Creates an isolated virtual environment at the target path using venv or uv.
    Ensures pip is properly seeded and functional.
    Returns (success, message, python_executable_path).
    """
    env_path = Path(env_path_str).resolve()
    python_exe = get_venv_python(env_path)

    # 1. If environment already exists and has python executable, check pip and reuse
    if python_exe.exists():
        ensure_pip_installed(python_exe)
        return True, f"Using existing virtual environment at {env_path}", python_exe

    env_path.mkdir(parents=True, exist_ok=True)

    # 2. Try fast creation with `uv venv --seed` if available
    if use_uv:
        code, stdout, stderr = run_cmd(["uv", "venv", "--seed", str(env_path)])
        if code == 0 and python_exe.exists():
            ensure_pip_installed(python_exe)
            return True, f"Created virtual environment using uv (seeded) at {env_path}", python_exe

    # 3. Fallback to standard Python `venv` module
    try:
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(env_path)
        if python_exe.exists():
            ensure_pip_installed(python_exe)
            return True, f"Created virtual environment using standard venv at {env_path}", python_exe
        else:
            return False, f"venv completed but Python binary missing at {python_exe}", python_exe
    except Exception as e:
        return False, f"Failed to create virtual environment: {str(e)}", python_exe
