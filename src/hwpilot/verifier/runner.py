"""Runtime environment verification runner."""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Tuple
from hwpilot.utils.subprocess_utils import run_cmd

VERIFICATION_SCRIPT = """
import sys
import json

results = {}

# Test 1: Import PyTorch
try:
    import torch
    results["Python"] = {"status": True, "message": f"Python {sys.version.split()[0]}"}
    results["PyTorch"] = {"status": True, "message": f"v{torch.__version__}"}
except Exception as e:
    results["Python"] = {"status": True, "message": f"Python {sys.version.split()[0]}"}
    results["PyTorch"] = {"status": False, "message": f"Failed to import PyTorch: {str(e)}"}
    print(json.dumps(results))
    sys.exit(0)

# Test 2: CUDA runtime version
cuda_version = getattr(torch.version, 'cuda', None)
if cuda_version:
    results["CUDA runtime"] = {"status": True, "message": f"CUDA {cuda_version}"}
else:
    results["CUDA runtime"] = {"status": True, "message": "CPU Build (no CUDA runtime)"}

# Test 3: CUDA availability
cuda_available = torch.cuda.is_available()
results["CUDA available"] = {"status": cuda_available, "message": "Yes" if cuda_available else "No"}

# Test 4: GPU detection
if cuda_available:
    try:
        device_count = torch.cuda.device_count()
        gpu_name = torch.cuda.get_device_name(0)
        results["GPU detected"] = {"status": True, "message": f"{gpu_name} ({device_count} device(s))"}
        results["GPU name"] = {"status": True, "message": gpu_name}
    except Exception as e:
        results["GPU detected"] = {"status": False, "message": f"Error querying GPU: {str(e)}"}
else:
    results["GPU detected"] = {"status": True, "message": "N/A (CPU Mode)"}

# Test 5: Real GPU tensor computation
if cuda_available:
    try:
        x = torch.randn(100, 100, device="cuda")
        y = x @ x
        torch.cuda.synchronize()
        val = float(y[0, 0].item())
        results["GPU computation"] = {"status": True, "message": "Matrix multiplication on GPU passed"}
    except Exception as e:
        results["GPU computation"] = {"status": False, "message": f"GPU tensor computation failed: {str(e)}"}
else:
    try:
        x = torch.randn(100, 100)
        y = x @ x
        results["GPU computation"] = {"status": True, "message": "CPU tensor computation passed"}
    except Exception as e:
        results["GPU computation"] = {"status": False, "message": f"CPU tensor computation failed: {str(e)}"}

print(json.dumps(results))
"""


def verify_environment(python_exe: Path) -> Tuple[bool, Dict[str, Any]]:
    """
    Executes runtime verification tests inside the target virtual environment.
    Returns (all_passed, results_dict).
    """
    if not python_exe.exists():
        return False, {
            "Environment": {
                "status": False,
                "message": f"Target Python executable does not exist at {python_exe}"
            }
        }

    code, stdout, stderr = run_cmd([str(python_exe), "-c", VERIFICATION_SCRIPT], timeout=60)
    if code != 0 or not stdout:
        return False, {
            "Runtime Verification": {
                "status": False,
                "message": f"Verification execution failed (code {code}). Stderr: {stderr}"
            }
        }

    try:
        results = json.loads(stdout)
        all_passed = all(item.get("status", False) for item in results.values())
        return all_passed, results
    except Exception as e:
        return False, {
            "JSON Parse": {
                "status": False,
                "message": f"Failed to parse verification output: {str(e)}\nOutput: {stdout}"
            }
        }
