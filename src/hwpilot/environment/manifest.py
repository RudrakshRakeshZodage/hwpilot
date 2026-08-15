"""Persistent environment manifest and configuration writer."""

import json
import datetime
from pathlib import Path
from typing import Dict, Any, List
from hwpilot.models.hardware import SystemReport
from hwpilot.models.plan import InstallationPlan
from hwpilot.models.manifest_model import EnvironmentManifest
from hwpilot import __version__ as HWPILOT_VERSION


def create_persistent_manifest(
    env_path_str: str,
    report: SystemReport,
    plan: InstallationPlan,
    verification_results: Dict[str, Any],
    install_logs: List[str]
) -> Path:
    """
    Creates persistent environment directory metadata:
    - <env_path>/config/hardware.json
    - <env_path>/config/environment.json
    - <env_path>/logs/install.log
    - <env_path>/manifest.json
    """
    env_dir = Path(env_path_str).resolve()
    config_dir = env_dir / "config"
    logs_dir = env_dir / "logs"

    config_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    # 1. hardware.json
    hardware_data = {
        "cpu": report.cpu.to_dict(),
        "gpu": report.gpu.to_dict(),
        "driver": report.driver.to_dict(),
    }
    with open(config_dir / "hardware.json", "w", encoding="utf-8") as f:
        json.dump(hardware_data, f, indent=2)

    # 2. environment.json
    env_data = {
        "os": report.os.to_dict(),
        "python": report.python.to_dict(),
        "backend": plan.backend,
        "framework": plan.framework,
        "framework_version": plan.framework_version,
        "cuda_runtime_version": plan.cuda_runtime_version,
        "index_url": plan.index_url,
    }
    with open(config_dir / "environment.json", "w", encoding="utf-8") as f:
        json.dump(env_data, f, indent=2)

    # 3. logs/install.log
    with open(logs_dir / "install.log", "w", encoding="utf-8") as f:
        f.write(f"=== HwPilot Setup Log [{timestamp}] ===\n\n")
        for entry in install_logs:
            f.write(entry + "\n\n")

    # 4. manifest.json
    packages_list = [pkg.to_dict() for pkg in plan.packages]
    manifest = EnvironmentManifest(
        hwpilot_version=HWPILOT_VERSION,
        created_at=timestamp,
        env_path=str(env_dir),
        backend=plan.backend,
        framework=plan.framework,
        framework_version=plan.framework_version,
        python_version=plan.python_version,
        cuda_runtime_version=plan.cuda_runtime_version,
        hardware=hardware_data,
        os=report.os.to_dict(),
        packages_installed=packages_list,
        verification_results=verification_results,
    )

    manifest_path = env_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest.to_dict(), f, indent=2)

    return manifest_path
