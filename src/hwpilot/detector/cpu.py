"""CPU detection routines."""

import platform
import os
import sys
from hwpilot.models.hardware import CPUInfo

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def detect_cpu() -> CPUInfo:
    """Detects CPU architecture, cores, model name, and RAM."""
    arch = platform.machine() or platform.processor() or "x86_64"
    model = platform.processor() or "Unknown CPU"

    # Refine model name on Windows / Linux if platform.processor() is generic
    if sys.platform.startswith("win32"):
        model_env = os.environ.get("PROCESSOR_IDENTIFIER", "")
        if model_env:
            model = model_env
    elif sys.platform.startswith("linux"):
        try:
            with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
                for line in f:
                    if "model name" in line:
                        model = line.split(":", 1)[1].strip()
                        break
        except Exception:
            pass

    # Cores and RAM
    logical_cores = os.cpu_count() or 1
    physical_cores = logical_cores

    ram_gb = 0.0
    if HAS_PSUTIL:
        try:
            physical_cores = psutil.cpu_count(logical=False) or logical_cores
            ram_bytes = psutil.virtual_memory().total
            ram_gb = round(ram_bytes / (1024 ** 3), 2)
        except Exception:
            pass

    # Clean up vendor identification
    model_lower = model.lower()
    vendor = "Unknown"
    if "intel" in model_lower:
        vendor = "Intel"
    elif "amd" in model_lower:
        vendor = "AMD"
    elif "apple" in model_lower or "arm" in model_lower:
        vendor = "Apple/ARM"

    return CPUInfo(
        vendor=vendor,
        model=model,
        architecture=arch,
        physical_cores=physical_cores,
        logical_cores=logical_cores,
        ram_gb=ram_gb,
    )
