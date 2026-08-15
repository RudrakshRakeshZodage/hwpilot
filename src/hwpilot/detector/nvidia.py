"""NVIDIA Driver and GPU detection routines via nvidia-smi and system tools."""

import xml.etree.ElementTree as ET
from typing import Tuple, Optional, Dict, Any
from hwpilot.models.hardware import GPUInfo, DriverInfo
from hwpilot.utils.subprocess_utils import run_cmd

# Known GPU architecture compute capability mappings if direct query fails or for fallback verification
COMPUTE_CAPABILITY_MAP = {
    "h100": "9.0",
    "h200": "9.0",
    "b200": "10.0",
    "rtx 4090": "8.9",
    "rtx 4080": "8.9",
    "rtx 4070": "8.9",
    "rtx 4060": "8.9",
    "rtx 4050": "8.9",
    "rtx 3090": "8.6",
    "rtx 3080": "8.6",
    "rtx 3070": "8.6",
    "rtx 3060": "8.6",
    "rtx 3050": "8.6",
    "a100": "8.0",
    "a10": "8.6",
    "a40": "8.6",
    "rtx 2080": "7.5",
    "rtx 2070": "7.5",
    "rtx 2060": "7.5",
    "gtx 1660": "7.5",
    "gtx 1650": "7.5",
    "gtx 1080": "6.1",
    "gtx 1070": "6.1",
    "gtx 1060": "6.1",
    "v100": "7.0",
    "t4": "7.5",
    "p100": "6.0",
    "k80": "3.7",
}


def detect_nvidia_driver() -> DriverInfo:
    """Queries NVIDIA driver version using nvidia-smi."""
    code, stdout, stderr = run_cmd(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"])
    if code != 0 or not stdout:
        return DriverInfo(
            vendor="NVIDIA",
            version=None,
            available=False,
            status_message="Unable to query NVIDIA driver because nvidia-smi is unavailable."
        )

    version_str = stdout.splitlines()[0].strip()
    return DriverInfo(
        vendor="NVIDIA",
        version=version_str,
        available=True,
        status_message=f"NVIDIA Driver version {version_str} detected."
    )


def detect_nvidia_gpu() -> GPUInfo:
    """Queries NVIDIA GPU model, VRAM, and Compute Capability using nvidia-smi."""
    # Query CSV format first
    cmd = ["nvidia-smi", "--query-gpu=gpu_name,memory.total,driver_version,compute_cap", "--format=csv,noheader,nounits"]
    code, stdout, stderr = run_cmd(cmd)

    if code != 0 or not stdout:
        # Fallback to general query
        cmd_fallback = ["nvidia-smi", "--query-gpu=gpu_name,memory.total", "--format=csv,noheader,nounits"]
        code, stdout, stderr = run_cmd(cmd_fallback)
        if code != 0 or not stdout:
            return GPUInfo(
                vendor="NVIDIA",
                model="NVIDIA GPU (unverified)",
                available=False,
                details={"error": "nvidia-smi unavailable"}
            )

    lines = stdout.splitlines()
    first_gpu = lines[0].split(",")
    gpu_name = first_gpu[0].strip()
    
    vram_mb = 0.0
    try:
        vram_mb = float(first_gpu[1].strip())
    except (IndexError, ValueError):
        pass
    vram_gb = round(vram_mb / 1024, 2)

    compute_cap = None
    if len(first_gpu) >= 4:
        cc_str = first_gpu[3].strip()
        if cc_str and cc_str.replace(".", "").isdigit():
            compute_cap = cc_str

    # Fallback compute capability lookup if not directly returned by query
    if not compute_cap:
        gpu_name_lower = gpu_name.lower()
        for key, cap in COMPUTE_CAPABILITY_MAP.items():
            if key in gpu_name_lower:
                compute_cap = cap
                break

    return GPUInfo(
        vendor="NVIDIA",
        model=gpu_name,
        vram_mb=vram_mb,
        vram_gb=vram_gb,
        compute_capability=compute_cap,
        available=True,
        details={"count": len(lines), "raw_query": stdout}
    )
