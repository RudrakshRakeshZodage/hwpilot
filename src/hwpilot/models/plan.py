"""Installation plan data models."""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class PackageSpec:
    name: str
    version: Optional[str] = None
    extra_index_url: Optional[str] = None
    options: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InstallationPlan:
    compatible: bool
    backend: str  # e.g., 'CUDA', 'CPU', 'ROCm', 'MPS'
    framework: str  # e.g., 'PyTorch'
    framework_version: str  # e.g., '2.4.1'
    python_version: str
    cuda_runtime_version: Optional[str] = None
    index_url: Optional[str] = None
    packages: List[PackageSpec] = field(default_factory=list)
    env_path: str = "./hwpilot-env"
    is_global: bool = False
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    driver_requirement_status: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "compatible": self.compatible,
            "backend": self.backend,
            "framework": self.framework,
            "framework_version": self.framework_version,
            "python_version": self.python_version,
            "cuda_runtime_version": self.cuda_runtime_version,
            "index_url": self.index_url,
            "packages": [pkg.to_dict() for pkg in self.packages],
            "env_path": self.env_path,
            "is_global": self.is_global,
            "warnings": self.warnings,
            "errors": self.errors,
            "driver_requirement_status": self.driver_requirement_status,
        }
