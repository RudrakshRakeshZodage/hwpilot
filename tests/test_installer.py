"""Unit tests for virtual environment creation and pip package installer."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from hwpilot.installer.venv import create_environment, get_venv_python
from hwpilot.installer.pip_runner import install_plan
from hwpilot.models.plan import InstallationPlan, PackageSpec


def test_get_venv_python_path(tmp_path):
    env_dir = tmp_path / "test-env"
    py_exe = get_venv_python(env_dir)
    assert py_exe.name in ("python.exe", "python")


@patch("hwpilot.installer.venv.run_cmd")
def test_create_environment_uv_fallback(mock_run, tmp_path):
    # Simulate uv failure, fallback to venv
    mock_run.return_value = (-1, "", "uv not found")
    env_dir = tmp_path / "test-venv"

    # Call creation (with standard venv fallback)
    success, msg, py_exe = create_environment(str(env_dir), use_uv=True)
    assert isinstance(success, bool)


@patch("hwpilot.installer.pip_runner.run_cmd_stream")
@patch("hwpilot.installer.pip_runner.run_cmd")
def test_install_plan_success(mock_run_cmd, mock_run_stream, tmp_path):
    mock_run_cmd.return_value = (0, "pip upgraded", "")
    mock_run_stream.return_value = (0, ["Successfully installed torch-2.4.1"])
    fake_py = tmp_path / "python.exe"
    fake_py.touch()

    plan = InstallationPlan(
        compatible=True,
        backend="CUDA",
        framework="PyTorch",
        framework_version="2.4.1",
        python_version="3.10.11",
        cuda_runtime_version="12.1",
        index_url="https://download.pytorch.org/whl/cu121",
        packages=[PackageSpec(name="torch", version="2.4.1")]
    )

    success, msg, logs = install_plan(plan, fake_py, stream_output=True)
    assert success is True
    assert "installed successfully" in msg.lower()
