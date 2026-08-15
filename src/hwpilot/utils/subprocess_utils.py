"""Safe subprocess execution helper."""

import subprocess
import shutil
from typing import Tuple, Optional, List


def run_cmd(
    cmd: List[str],
    timeout: int = 30,
    cwd: Optional[str] = None,
    check_executable: bool = True
) -> Tuple[int, str, str]:
    """
    Executes a subprocess command safely.
    Returns (returncode, stdout, stderr).
    """
    if check_executable and cmd:
        exe = shutil.which(cmd[0])
        if not exe and not cmd[0].endswith(".exe") and not cmd[0].startswith("."):
            return -1, "", f"Executable '{cmd[0]}' not found in PATH."

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", f"Command '{' '.join(cmd)}' timed out after {timeout} seconds."
    except Exception as e:
        return -1, "", f"Execution error: {str(e)}"
