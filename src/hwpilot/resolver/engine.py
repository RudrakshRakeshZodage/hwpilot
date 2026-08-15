"""HwPilot Compatibility Resolution Engine."""

from typing import Optional, Dict, Any, List
from hwpilot.models.hardware import SystemReport
from hwpilot.models.plan import InstallationPlan, PackageSpec
from hwpilot.metadata.store import load_metadata
from hwpilot.resolver.rules import is_driver_compatible, is_python_compatible


class CompatibilityResolver:
    """
    Hardware-aware ML compatibility resolver.
    Dynamically determines appropriate framework versions, CUDA runtimes,
    and package specs without hardcoded hardware strings.
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None):
        self.metadata = metadata or load_metadata()

    def resolve(
        self,
        report: SystemReport,
        target_framework: str = "PyTorch",
        env_path: str = "./hwpilot-env",
        is_global: bool = False
    ) -> InstallationPlan:
        warnings: List[str] = []
        errors: List[str] = []
        driver_status_msg: Optional[str] = None

        # 1. OS & Architecture Compatibility Check
        os_sys = report.os.platform_system
        os_arch = report.os.architecture.lower()

        if os_sys not in ("Windows", "Linux", "Darwin"):
            errors.append(f"Unsupported operating system: {os_sys}")
        if os_arch not in ("x86_64", "amd64", "x64", "arm64", "aarch64"):
            errors.append(f"Unsupported system architecture: {os_arch}")

        # 2. Framework Metadata Lookup
        fw_meta = self.metadata.get("frameworks", {}).get(target_framework)
        if not fw_meta:
            errors.append(f"Framework '{target_framework}' not configured in compatibility matrix.")
            return InstallationPlan(
                compatible=False,
                backend="Unknown",
                framework=target_framework,
                framework_version="Unknown",
                python_version=report.python.version,
                env_path=env_path,
                is_global=is_global,
                errors=errors,
            )

        # 3. Python Version Compatibility
        supported_pythons = fw_meta.get("python_supported", [])
        if not is_python_compatible(report.python.version, supported_pythons):
            warnings.append(
                f"Python version {report.python.version} is outside tested framework range {supported_pythons}."
            )

        # 4. Backend & CUDA Resolution
        selected_backend = "CPU"
        selected_cuda_version: Optional[str] = None
        selected_index_url: Optional[str] = None
        selected_fw_version = fw_meta.get("default_version", "2.4.1")
        selected_packages_raw: List[str] = ["torch", "torchvision", "torchaudio"]

        driver_reqs = self.metadata.get("nvidia_driver_requirements", {})
        cuda_candidates = fw_meta.get("cuda_runtimes", [])

        is_nvidia_gpu = report.gpu.vendor.lower() == "nvidia" and report.gpu.available

        if is_nvidia_gpu:
            driver_ver = report.driver.version
            os_key = "Windows" if os_sys == "Windows" else "Linux"

            # Search candidate CUDA runtimes in order of preference
            matched_cuda = None
            highest_req_driver = None

            for candidate in cuda_candidates:
                cuda_ver = candidate.get("cuda_version")
                if not cuda_ver:
                    continue  # skip CPU fallback candidate in GPU search

                # Driver check for this CUDA version
                req_driver_dict = driver_reqs.get(cuda_ver, {})
                req_min_driver = req_driver_dict.get(os_key)

                if req_min_driver and not highest_req_driver:
                    highest_req_driver = req_min_driver

                if report.driver.available and is_driver_compatible(driver_ver, req_min_driver):
                    matched_cuda = candidate
                    break

            if matched_cuda:
                selected_backend = "CUDA"
                selected_cuda_version = matched_cuda["cuda_version"]
                selected_fw_version = matched_cuda.get("pytorch_version", selected_fw_version)
                selected_index_url = matched_cuda.get("index_url")
                selected_packages_raw = matched_cuda.get("packages", selected_packages_raw)
            else:
                # Incompatible or missing driver
                selected_backend = "CPU"
                if not report.driver.available:
                    driver_status_msg = (
                        "⚠ Unable to verify NVIDIA driver because nvidia-smi is unavailable. "
                        "Falling back to CPU PyTorch build."
                    )
                    warnings.append(driver_status_msg)
                else:
                    driver_status_msg = (
                        f"⚠ Installed NVIDIA driver ({driver_ver}) appears incompatible with requested CUDA runtimes "
                        f"(Minimum required driver for latest CUDA: {highest_req_driver}). "
                        "HwPilot will not modify system drivers. Falling back to CPU backend. "
                        "Please update your NVIDIA driver and run `hwpilot doctor`."
                    )
                    warnings.append(driver_status_msg)
        elif report.gpu.vendor.lower() == "apple":
            selected_backend = "MPS"
            # PyTorch standard wheels support MPS out of the box
            selected_index_url = None
        else:
            selected_backend = "CPU"
            # Find CPU candidate
            for candidate in cuda_candidates:
                if candidate.get("cuda_version") is None:
                    selected_index_url = candidate.get("index_url")
                    break

        # 5. Build Package Specifications
        packages: List[PackageSpec] = []
        for pkg in selected_packages_raw:
            packages.append(
                PackageSpec(
                    name=pkg,
                    version=selected_fw_version if pkg == "torch" else None,
                    extra_index_url=selected_index_url
                )
            )

        is_compatible = len(errors) == 0

        return InstallationPlan(
            compatible=is_compatible,
            backend=selected_backend,
            framework=target_framework,
            framework_version=selected_fw_version,
            python_version=report.python.version,
            cuda_runtime_version=selected_cuda_version,
            index_url=selected_index_url,
            packages=packages,
            env_path=env_path,
            is_global=is_global,
            warnings=warnings,
            errors=errors,
            driver_requirement_status=driver_status_msg,
        )


def resolve_environment(
    report: SystemReport,
    target_framework: str = "PyTorch",
    env_path: str = "./hwpilot-env",
    is_global: bool = False
) -> InstallationPlan:
    resolver = CompatibilityResolver()
    return resolver.resolve(report, target_framework=target_framework, env_path=env_path, is_global=is_global)
