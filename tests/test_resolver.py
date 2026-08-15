"""Unit tests for compatibility resolver engine."""

import pytest
from hwpilot.models.hardware import SystemReport, CPUInfo, GPUInfo, DriverInfo, OSInfo, PythonInfo
from hwpilot.resolver.engine import CompatibilityResolver


def build_mock_report(
    gpu_available=True,
    driver_version="535.104.05",
    driver_available=True,
    os_sys="Windows",
    py_ver="3.10.11"
):
    return SystemReport(
        cpu=CPUInfo(vendor="Intel", model="Core i9", physical_cores=8, logical_cores=16, ram_gb=32.0),
        gpu=GPUInfo(vendor="NVIDIA", model="RTX 4060", vram_gb=8.0, compute_capability="8.9", available=gpu_available),
        driver=DriverInfo(vendor="NVIDIA", version=driver_version if driver_available else None, available=driver_available),
        os=OSInfo(name="Windows 11", architecture="x64", platform_system=os_sys),
        python=PythonInfo(version=py_ver, version_tuple=(3, 10, 11)),
    )


def test_resolver_nvidia_cuda_success():
    report = build_mock_report(driver_version="535.104.05")
    resolver = CompatibilityResolver()
    plan = resolver.resolve(report)

    assert plan.compatible is True
    assert plan.backend == "CUDA"
    assert plan.cuda_runtime_version in ("12.4", "12.1", "11.8")
    assert plan.framework == "PyTorch"
    assert len(plan.packages) >= 1
    assert any(pkg.name == "torch" for pkg in plan.packages)


def test_resolver_incompatible_driver_fallback_cpu():
    # Very old NVIDIA driver (e.g., 384.11) insufficient for CUDA 11/12
    report = build_mock_report(driver_version="384.11")
    resolver = CompatibilityResolver()
    plan = resolver.resolve(report)

    assert plan.backend == "CPU"
    assert any("NVIDIA driver" in w for w in plan.warnings)


def test_resolver_missing_nvidia_smi_fallback_cpu():
    report = build_mock_report(driver_available=False)
    resolver = CompatibilityResolver()
    plan = resolver.resolve(report)

    assert plan.backend == "CPU"
    assert any("nvidia-smi is unavailable" in w for w in plan.warnings)


def test_resolver_cpu_only_machine():
    report = build_mock_report(gpu_available=False, driver_available=False)
    report.gpu.vendor = "None"
    resolver = CompatibilityResolver()
    plan = resolver.resolve(report)

    assert plan.backend == "CPU"
    assert plan.cuda_runtime_version is None
    assert plan.compatible is True


def test_resolver_unsupported_os():
    report = build_mock_report(os_sys="FreeBSD")
    resolver = CompatibilityResolver()
    plan = resolver.resolve(report)

    assert plan.compatible is False
    assert any("Unsupported operating system" in err for err in plan.errors)
