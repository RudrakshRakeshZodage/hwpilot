"""Unit tests for HwPilot CLI subcommands and JSON outputs."""

import sys
import json
import pytest
from unittest.mock import patch, MagicMock
from hwpilot.cli import main


def test_cli_help(capsys):
    with patch.object(sys, "argv", ["hwpilot", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "HwPilot" in captured.out or "usage:" in captured.out


@patch("hwpilot.cli.detect_system")
def test_cli_detect_json(mock_detect, capsys):
    from hwpilot.models.hardware import SystemReport
    mock_detect.return_value = SystemReport()

    with patch.object(sys, "argv", ["hwpilot", "detect", "--json"]):
        main()

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "cpu" in data
    assert "gpu" in data
    assert "driver" in data


@patch("hwpilot.cli.detect_system")
@patch("hwpilot.cli.resolve_environment")
def test_cli_plan_json(mock_resolve, mock_detect, capsys):
    from hwpilot.models.hardware import SystemReport
    from hwpilot.models.plan import InstallationPlan

    mock_detect.return_value = SystemReport()
    mock_resolve.return_value = InstallationPlan(
        compatible=True,
        backend="CUDA",
        framework="PyTorch",
        framework_version="2.4.1",
        python_version="3.10.11"
    )

    with patch.object(sys, "argv", ["hwpilot", "plan", "--json"]):
        main()

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "system" in data
    assert "plan" in data
    assert data["plan"]["backend"] == "CUDA"


@patch("hwpilot.cli.detect_system")
@patch("hwpilot.cli.resolve_environment")
def test_cli_check_json(mock_resolve, mock_detect, capsys):
    from hwpilot.models.hardware import SystemReport
    from hwpilot.models.plan import InstallationPlan

    mock_detect.return_value = SystemReport()
    mock_resolve.return_value = InstallationPlan(
        compatible=True,
        backend="CUDA",
        framework="PyTorch",
        framework_version="2.4.1",
        python_version="3.10.11"
    )

    with patch.object(sys, "argv", ["hwpilot", "check", "--json"]):
        main()

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "suitable" in data
    assert "backend" in data


def test_cli_info_json(capsys):
    with patch.object(sys, "argv", ["hwpilot", "info", "--json"]):
        main()

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["name"] == "HwPilot"
    assert "version" in data
