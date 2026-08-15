"""Safe subprocess execution helper with real-time streaming support."""

import sys
import subprocess
import shutil
from typing import Tuple, Optional, List, Callable


def run_cmd(
    cmd: List[str],
    timeout: int = 600,
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


def run_cmd_stream(
    cmd: List[str],
    cwd: Optional[str] = None,
    line_callback: Optional[Callable[[str], None]] = None
) -> Tuple[int, List[str]]:
    """
    Executes a subprocess command and streams stdout lines in real-time,
    handling both newline (\\n) and carriage return (\\r) progress updates.
    Returns (returncode, lines_captured).
    """
    if cmd:
        exe = shutil.which(cmd[0])
        if not exe and not cmd[0].endswith(".exe") and not cmd[0].startswith("."):
            return -1, [f"Executable '{cmd[0]}' not found in PATH."]

    captured_lines: List[str] = []
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=cwd,
            bufsize=1,
            universal_newlines=True
        )

        buffer = ""
        if proc.stdout:
            while True:
                chunk = proc.stdout.read(64)
                if not chunk and proc.poll() is not None:
                    break
                if not chunk:
                    continue
                buffer += chunk

                while "\n" in buffer or "\r" in buffer:
                    idx_r = buffer.find("\r")
                    idx_n = buffer.find("\n")
                    if idx_r != -1 and (idx_n == -1 or idx_r < idx_n):
                        line = buffer[:idx_r]
                        buffer = buffer[idx_r + 1:]
                    else:
                        line = buffer[:idx_n]
                        buffer = buffer[idx_n + 1:]

                    line_clean = line.strip()
                    if line_clean:
                        captured_lines.append(line_clean)
                        if line_callback:
                            line_callback(line_clean)
                        else:
                            print(f"  {line_clean}", flush=True)

            # Flush remaining buffer if any
            line_clean = buffer.strip()
            if line_clean:
                captured_lines.append(line_clean)
                if line_callback:
                    line_callback(line_clean)

        returncode = proc.wait()
        return returncode, captured_lines
    except Exception as e:
        return -1, [f"Stream execution error: {str(e)}"]
