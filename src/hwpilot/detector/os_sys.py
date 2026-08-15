"""Operating System and Python runtime detection routines."""

import platform
import sys
from hwpilot.models.hardware import OSInfo, PythonInfo


def detect_os() -> OSInfo:
    """Detects operating system name, version, architecture, and system type."""
    system = platform.system()  # Windows, Linux, Darwin
    release = platform.release()
    version = platform.version()
    arch = platform.machine() or "x64"

    os_name = system
    if system == "Windows":
        os_name = f"Windows {release} {arch}"
    elif system == "Linux":
        os_name = f"Linux {release} ({arch})"
    elif system == "Darwin":
        os_name = f"macOS {release} ({arch})"

    return OSInfo(
        name=os_name,
        version=version,
        release=release,
        architecture=arch,
        platform_system=system,
    )


def detect_python() -> PythonInfo:
    """Detects Python version and executable path."""
    v_info = sys.version_info
    v_str = f"{v_info.major}.{v_info.minor}.{v_info.micro}"
    arch, _ = platform.architecture()

    return PythonInfo(
        version=v_str,
        version_tuple=(v_info.major, v_info.minor, v_info.micro),
        executable=sys.executable,
        architecture=arch,
    )
