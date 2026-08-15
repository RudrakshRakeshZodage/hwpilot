"""Unit tests for runtime environment verifier."""

import pytest
import json
from unittest.mock import patch
from hwpilot.verifier.runner import verify_environment


@patch("hwpilot.verifier.runner.run_cmd")
def test_verify_environment_success(mock_run, tmp_path):
    fake_results = {
        "Python": {"status": True, "message": "Python 3.10.11"},
        "PyTorch": {"status": True, "message": "v2.4.1"},
        "CUDA runtime": {"status": True, "message": "CUDA 12.1"},
        "CUDA available": {"status": True, "message": "Yes"},
        "GPU detected": {"status": True, "message": "NVIDIA GeForce RTX 4060"},
        "GPU computation": {"status": True, "message": "Passed"}
    }
    mock_run.return_value = (0, json.dumps(fake_results), "")

    fake_py = tmp_path / "python.exe"
    fake_py.touch()

    all_passed, results = verify_environment(fake_py)
    assert all_passed is True
    assert results["PyTorch"]["status"] is True
    assert results["GPU computation"]["status"] is True


@patch("hwpilot.verifier.runner.run_cmd")
def test_verify_environment_failure(mock_run, tmp_path):
    fake_results = {
        "PyTorch": {"status": True, "message": "v2.4.1"},
        "GPU computation": {"status": False, "message": "CUDA error: out of memory"}
    }
    mock_run.return_value = (0, json.dumps(fake_results), "")

    fake_py = tmp_path / "python.exe"
    fake_py.touch()

    all_passed, results = verify_environment(fake_py)
    assert all_passed is False
    assert results["GPU computation"]["status"] is False
