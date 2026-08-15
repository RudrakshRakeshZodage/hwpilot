"""Unified GPU Detection Dispatcher."""

import sys
from hwpilot.models.hardware import GPUInfo
from hwpilot.detector.nvidia import detect_nvidia_gpu, detect_nvidia_driver


def detect_gpu() -> GPUInfo:
    """
    Unified GPU detector dispatcher.
    Checks NVIDIA GPUs, with extensible support for AMD, Intel, Apple MPS, or CPU-only.
    """
    # 1. Check NVIDIA GPU
    nvidia_gpu = detect_nvidia_gpu()
    if nvidia_gpu.available:
        return nvidia_gpu

    # 2. Check Apple Silicon MPS (Darwin arm64)
    if sys.platform == "darwin":
        import platform
        if platform.machine() in ("arm64", "aarch64"):
            return GPUInfo(
                vendor="Apple",
                model="Apple Silicon GPU (MPS)",
                vram_mb=0.0,
                vram_gb=0.0,
                available=True,
                architecture="arm64",
                details={"backend": "MPS"}
            )

    # 3. Default fallback: CPU-only / GPU unavailable
    return GPUInfo(
        vendor="None",
        model="No compatible dedicated GPU detected (CPU mode)",
        vram_mb=0.0,
        vram_gb=0.0,
        available=False,
        details={"status": "CPU Fallback"}
    )
