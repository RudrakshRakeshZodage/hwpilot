<div align="center">
  <img src="main.png" alt="HwPilot Banner" width="100%" />
</div>

# HwPilot — Hardware-aware ML Environment Setup & Compatibility Manager

[![PyPI version](https://img.shields.io/pypi/v/hwpilot.svg?style=flat-square&color=blue)](https://pypi.org/project/hwpilot/)
[![Python Version](https://img.shields.io/pypi/pyversions/hwpilot.svg?style=flat-square&color=brightgreen)](https://pypi.org/project/hwpilot/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Author: Rudraksh Rakesh Zodage](https://img.shields.io/badge/Author-Rudraksh%20Rakesh%20Zodage-orange.svg?style=flat-square)](https://github.com/RudrakshRakeshZodage)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Rudraksh%20Zodage-blue?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/rudraksh-zodage-/)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97%20HuggingFace-Rudraksh%20Zodage-yellow?style=flat-square)](https://huggingface.co/rudrakshrakeshzodage)

> **HwPilot — Hardware-aware ML environment setup and compatibility manager.**
> 
> *Detect my hardware. Resolve the correct ML environment. Ask me once. Install it safely. Verify that it actually works.*

---

## 👨‍💻 Created & Maintained By

**Rudraksh Rakesh Zodage**  
AI / Machine Learning Engineer & Developer

- **Email**: [rudrakshrakeshzodage@gmail.com](mailto:rudrakshrakeshzodage@gmail.com)
- **GitHub**: [github.com/RudrakshRakeshZodage](https://github.com/RudrakshRakeshZodage/)
- **LinkedIn**: [linkedin.com/in/rudraksh-zodage-](https://www.linkedin.com/in/rudraksh-zodage-/)
- **HuggingFace**: [huggingface.co/rudrakshrakeshzodage](https://huggingface.co/rudrakshrakeshzodage)

---

## 🔄 End-to-End System Sequence & Architecture

```mermaid
sequenceDiagram
    autonumber
    actor User as 💻 User (CLI)
    participant Detector as 🔍 Hardware Detector
    participant Resolver as ⚖️ Compatibility Engine
    participant Venv as 📦 Environment Manager
    participant PyTorch as 🌐 PyTorch Wheel Index
    participant Verifier as 🧪 GPU Tensor Verifier

    User->>Detector: Execute `hwpilot setup -y`
    activate Detector
    Detector->>Detector: Probe CPU, GPU (nvidia-smi), OS & Python
    Detector-->>Resolver: Return Hardware Specs (RTX 4060, Driver 610.74, Python 3.13)
    deactivate Detector

    activate Resolver
    Resolver->>Resolver: Evaluate Driver vs CUDA Matrix (defaults.json)
    Resolver-->>User: Display Compatibility Plan (PyTorch 2.6.0 + CUDA 12.4)
    deactivate Resolver

    User->>Venv: Initialize Isolated Virtual Environment
    activate Venv
    Venv->>Venv: Create `./hwpilot-env` (Seeded with pip/wheel)
    
    Venv->>PyTorch: Request PyTorch CUDA 12.4 Wheel Packages
    activate PyTorch
    PyTorch-->>Venv: Stream Download (~2.53 GB) & Unpack CUDA DLLs
    deactivate PyTorch
    deactivate Venv

    Venv->>Verifier: Trigger Runtime Verification Suite
    activate Verifier
    Verifier->>Verifier: Import torch & Validate CUDA Device Available
    Verifier->>Verifier: Execute Matrix Multiplication Tensor Math on GPU
    Verifier-->>User: Runtime Verification PASSED (GPU Accelerated)
    deactivate Verifier

    Venv->>User: Save `manifest.json` & Output Environment Activation Path
```

---

## 🔥 What is HwPilot?

No cap, setting up PyTorch and CUDA across different GPUs and laptops is a major headache. Broken drivers, incompatible wheels, and CUDA errors ruin the vibe.

**HwPilot** solves this automatically:
- 🤖 **Auto-detects your rig**: Scans your CPU, GPU, VRAM, NVIDIA drivers, and OS.
- ⚡ **Smart Resolution**: Finds the exact PyTorch + CUDA build tailored for your machine.
- 🛡️ **Clean & Safe**: Creates an isolated `./hwpilot-env` without touching system drivers.
- ✅ **Real GPU Verification**: Runs actual GPU tensor math before saying it's ready. No fake green checks.

---

## ⚡ Quick Start

### Installation

```bash
pip install hwpilot
```

> **Note for Windows Users**: If running global `pip install hwpilot`, you can run via `python -m hwpilot <command>` OR add Python Scripts to your PowerShell PATH for the current session:
> ```powershell
> $env:Path += ";$env:APPDATA\Python\Python313\Scripts"
> ```

### Quick Setup

Auto-detect your hardware, resolve compatible PyTorch/CUDA wheels, create an isolated virtual environment, and verify GPU compute in one command:

```bash
hwpilot setup -y
```

*(or via python module)*:
```bash
python -m hwpilot setup -y
```

> **Flags**:
> - `-y`, `--yes`: Automatically accept and proceed without prompt.
> - `-p`, `--path <DIR>`: Custom environment path (default: `./hwpilot-env`).

---

## 🚀 Key Commands & CLI Reference

| Command | Description |
| :--- | :--- |
| `hwpilot detect` | Inspect hardware (CPU, GPU, VRAM, Compute Capability, Driver, OS, Python). |
| `hwpilot check` | Evaluate whether the machine meets requirements for ML workloads. |
| `hwpilot plan` | Preview compatibility resolution and package specs without modifying system. |
| `hwpilot setup` | Complete end-to-end setup workflow (detect → resolve → confirm → venv → install → verify → manifest). |
| `hwpilot verify` | Perform real GPU matrix multiplication tensor test in an existing environment. |
| `hwpilot doctor` | Generate a comprehensive diagnostic and troubleshooting report. |
| `hwpilot update` | Refresh cached compatibility metadata from remote index. |
| `hwpilot info` | Display HwPilot version, author profiles, and metadata information. |

### Command Flags

- `--pytorch <VER>` / `--torch <VER>`: Suggest specific PyTorch framework version (e.g. `2.4.1`, `2.3.1`).
- `--cuda <VER>`: Suggest specific CUDA runtime build version (e.g. `12.4`, `12.1`, `11.8`, `cpu`).
- `--json`: Output machine-readable JSON format for programmatic use.
- `-y`, `--yes`: Bypass interactive confirmation prompt.
- `-p`, `--path <DIR>`: Custom target environment path (default: `./hwpilot-env`).
- `--global`: Install directly into current Python environment (requires explicit opt-in).
- `-v`, `--verbose`: Enable debug logging.

---

## 🛡️ Safety & Security Principles

1. **Driver Integrity**: HwPilot **never** modifies or replaces system graphics drivers.
2. **Environment Isolation**: Prefers isolated project environments (`./hwpilot-env`).
3. **No Guessing**: Uses strict declarative compatibility matrices.
4. **Empirical Verification**: Verifies GPU runtime with actual tensor operations.

---

## 📁 Environment Manifest Structure

Upon successful setup, HwPilot generates an environment audit manifest:

```text
hwpilot-env/
├── config/
│   ├── hardware.json      # Hardware specs (CPU, GPU, Driver)
│   └── environment.json   # Resolved backend, CUDA runtime, framework versions
├── logs/
│   └── install.log        # Package installation transcript
└── manifest.json          # Environment state & verification results
```

---

## 🧪 Testing & Development

```bash
git clone https://github.com/RudrakshRakeshZodage/hwpilot.git
cd hwpilot
pip install -e .[dev]
pytest
```

---

## 🤝 Contributing

Contributions to **HwPilot** are welcome! Whether you are reporting a bug, adding hardware compatibility rules, or improving documentation, please read our [CONTRIBUTING.md](file:///d:/Rudraksh/College/app/hwpilot/CONTRIBUTING.md) guide.

### Quick Workflow for Contributors
1. Fork and clone the repository: `git clone https://github.com/RudrakshRakeshZodage/hwpilot.git`
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `pip install -e .[dev]`
4. Ensure test suite passes: `pytest`
5. Open a Pull Request on [GitHub](https://github.com/RudrakshRakeshZodage/hwpilot/pulls).

---

## 👤 Author & Maintainer Profile

Created, architected, and maintained by **Rudraksh Rakesh Zodage**.

- **Email**: [rudrakshrakeshzodage@gmail.com](mailto:rudrakshrakeshzodage@gmail.com)
- **GitHub**: [github.com/RudrakshRakeshZodage](https://github.com/RudrakshRakeshZodage/)
- **LinkedIn**: [linkedin.com/in/rudraksh-zodage-](https://www.linkedin.com/in/rudraksh-zodage-/)
- **HuggingFace**: [huggingface.co/rudrakshrakeshzodage](https://huggingface.co/rudrakshrakeshzodage)

---

## 📜 License & Copyright

This project is licensed under the terms of the **MIT License**.

```text
Copyright (c) 2026 Rudraksh Rakesh Zodage

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

For full license details, see the [LICENSE](file:///d:/Rudraksh/College/app/hwpilot/LICENSE) file.
