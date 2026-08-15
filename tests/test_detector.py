"""Unit tests for hardware and system detection with mocked subprocess calls."""

import pytest
from unittest.mock import patch, MagicMock
from hwpilot.detector.cpu import detect_cpu
from hwpilot.detector.os_sys import detect_os, detect_python
from hwpilot.detector.nvidia import detect_nvidia_driver, detect_nvidia_gpu
from hwpilot.detector.gpu import detect_gpu


def test_detect_cpu():
    cpu = detect_cpu()
    assert cpu.vendor in ("Intel", "AMD", "Apple/ARM", "Unknown")
    assert cpu.logical_cores >= 1
    assert cpu.architecture != ""


def test_detect_os_and_python():
    os_info = detect_os()
    assert os_info.platform_system in ("Windows", "Linux", "Darwin")
    assert os_info.architecture != ""

    py_info = detect_python()
    assert py_info.version_tuple[0] >= 3
    assert py_info.executable != ""


@patch("hwpilot.detector.nvidia.run_cmd")
def test_detect_nvidia_driver_success(mock_run):
    mock_run.return_value = (0, "535.104.05", "")
    driver = detect_nvidia_driver()
    assert driver.available is True
    assert driver.version == "535.104.05"
    assert "detected" in driver.status_message.lower()


@patch("hwpilot.detector.nvidia.run_cmd")
def test_detect_nvidia_driver_missing_nvidia_smi(mock_run):
    mock_run.return_value = (-1, "", "Executable 'nvidia-smi' not found in PATH.")
    driver = detect_nvidia_driver()
    assert driver.available is False
    assert driver.version is None
    assert "unavailable" in driver.status_message.lower()


@patch("hwpilot.detector.nvidia.run_cmd")
def test_detect_nvidia_gpu_success(mock_run):
    mock_run.return_value = (0, "NVIDIA GeForce RTX 4060, 8192, 535.104, 8.9", "")
    gpu = detect_nvidia_gpu()
    assert gpu.available is True
    assert "RTX 4060" in gpu.model
    assert gpu.vram_gb == 8.0
    assert gpu.compute_capability == "8.9"


@patch("hwpilot.detector.nvidia.run_cmd")
def test_detect_nvidia_gpu_missing(mock_run):
    mock_run.return_value = (-1, "", "nvidia-smi unavailable")
    gpu = detect_nvidia_gpu()
    assert gpu.available is False
    assert "unverified" in gpu.model.lower() or "no" in gpu.model.lower()


@patch("hwpilot.detector.gpu.detect_nvidia_gpu")
def test_detect_gpu_fallback_cpu(mock_detect_nv):
    mock_detect_nv.return_value = MagicMock(available=False, vendor="None", model="No GPU")
    gpu = detect_gpu()
    assert gpu.available is False or gpu.vendor == "Apple"
