"""Persistent environment manifest data model."""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


@dataclass
class EnvironmentManifest:
    hwpilot_version: str
    created_at: str
    env_path: str
    backend: str
    framework: str
    framework_version: str
    python_version: str
    cuda_runtime_version: Optional[str]
    hardware: Dict[str, Any]
    os: Dict[str, Any]
    packages_installed: List[Dict[str, Any]]
    verification_results: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
