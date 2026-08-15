"""Hardware and system information dataclasses."""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any


@dataclass
class CPUInfo:
    vendor: str = "Unknown"
    model: str = "Unknown CPU"
    architecture: str = "Unknown"
    physical_cores: int = 0
    logical_cores: int = 0
    ram_gb: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GPUInfo:
    vendor: str = "Unknown"
    model: str = "Unknown GPU"
    vram_mb: float = 0.0
    vram_gb: float = 0.0
    compute_capability: Optional[str] = None
    architecture: Optional[str] = None
    cuda_cores: Optional[int] = None
    available: bool = False
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DriverInfo:
    vendor: str = "NVIDIA"
    version: Optional[str] = None
    available: bool = False
    cuda_version_supported: Optional[str] = None
    status_message: str = "Driver check pending"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OSInfo:
    name: str = "Unknown OS"
    version: str = "Unknown"
    release: str = "Unknown"
    architecture: str = "Unknown"
    platform_system: str = "Unknown"  # Windows, Linux, Darwin

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PythonInfo:
    version: str = "Unknown"
    version_tuple: tuple = (0, 0, 0)
    executable: str = ""
    architecture: str = "Unknown"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["version_tuple"] = list(self.version_tuple)
        return d


@dataclass
class SystemReport:
    cpu: CPUInfo = field(default_factory=CPUInfo)
    gpu: GPUInfo = field(default_factory=GPUInfo)
    driver: DriverInfo = field(default_factory=DriverInfo)
    os: OSInfo = field(default_factory=OSInfo)
    python: PythonInfo = field(default_factory=PythonInfo)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cpu": self.cpu.to_dict(),
            "gpu": self.gpu.to_dict(),
            "driver": self.driver.to_dict(),
            "os": self.os.to_dict(),
            "python": self.python.to_dict(),
            "warnings": self.warnings,
        }
