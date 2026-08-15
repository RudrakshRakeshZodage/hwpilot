"""Compatibility comparison helper functions."""

from packaging.version import parse as parse_version, Version
from typing import Optional, Dict


def is_driver_compatible(installed_version: Optional[str], required_min_version: Optional[str]) -> bool:
    """
    Compares NVIDIA driver versions using semantic version parsing.
    Returns True if installed_version >= required_min_version.
    """
    if not installed_version or not required_min_version:
        return False

    try:
        inst_v = parse_version(installed_version)
        req_v = parse_version(required_min_version)
        return inst_v >= req_v
    except Exception:
        return False


def is_python_compatible(python_version: str, supported_versions: list) -> bool:
    """Checks if Python major.minor version is in the supported versions list."""
    try:
        p_ver = parse_version(python_version)
        p_short = f"{p_ver.major}.{p_ver.minor}"
        return p_short in supported_versions
    except Exception:
        return False
