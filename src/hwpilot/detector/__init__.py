"""Hardware and environment detector module."""

from hwpilot.detector.cpu import detect_cpu
from hwpilot.detector.os_sys import detect_os, detect_python
from hwpilot.detector.nvidia import detect_nvidia_driver, detect_nvidia_gpu
from hwpilot.detector.gpu import detect_gpu
from hwpilot.models.hardware import SystemReport


def detect_system() -> SystemReport:
    """Executes full hardware and system detection."""
    cpu_info = detect_cpu()
    os_info = detect_os()
    python_info = detect_python()
    gpu_info = detect_gpu()
    driver_info = detect_nvidia_driver()

    warnings = []
    if not gpu_info.available:
        warnings.append(f"GPU check: {gpu_info.model}")
    if gpu_info.vendor.lower() == "nvidia" and not driver_info.available:
        warnings.append(f"Driver check: {driver_info.status_message}")

    return SystemReport(
        cpu=cpu_info,
        gpu=gpu_info,
        driver=driver_info,
        os=os_info,
        python=python_info,
        warnings=warnings,
    )


__all__ = [
    "detect_cpu",
    "detect_os",
    "detect_python",
    "detect_nvidia_driver",
    "detect_nvidia_gpu",
    "detect_gpu",
    "detect_system",
]
