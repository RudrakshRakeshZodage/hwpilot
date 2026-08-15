# Contributing to HwPilot

Thank you for your interest in contributing to **HwPilot** — Hardware-aware ML environment setup and compatibility manager!

This project is created and maintained by **[Rudraksh Rakesh Zodage](https://github.com/RudrakshRakeshZodage)**.

We welcome contributions of all kinds: bug reports, hardware compatibility metadata updates, feature requests, documentation improvements, and code pull requests.

---

## 🛠️ Development Setup

### 1. Fork & Clone the Repository

```bash
git clone https://github.com/RudrakshRakeshZodage/hwpilot.git
cd hwpilot
```

### 2. Set Up a Virtual Environment & Install Development Dependencies

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -e .[dev]
```

### 3. Run the Test Suite

Before submitting changes, ensure all tests pass:

```bash
pytest
```

---

## 💡 How to Contribute

### 1. Adding Hardware Compatibility Rules
If a new GPU series, NVIDIA driver release, or PyTorch CUDA wheel build is released:
1. Update `src/hwpilot/metadata/defaults.json`.
2. Add corresponding test cases in `tests/test_resolver.py`.
3. Submit a Pull Request.

### 2. Reporting Issues
Please submit issues via [GitHub Issues](https://github.com/RudrakshRakeshZodage/hwpilot/issues) with:
- Operating system version (`Windows 11`, `Ubuntu 22.04`, etc.)
- GPU model & NVIDIA driver version (`nvidia-smi` output)
- Expected vs actual behavior
- Terminal output log

### 3. Pull Request Guidelines
- Follow PEP 8 guidelines for Python code.
- Ensure all hardware detector calls use mocks in unit tests so `pytest` passes on non-GPU CI runners.
- Keep commits concise and clear.

---

## 📜 Code of Conduct

Please be respectful and constructive in all issues, discussions, and pull request reviews.

---

## 📬 Contact & Support

Maintainer: **Rudraksh Rakesh Zodage**  
- **Email**: [rudrakshrakeshzodage@gmail.com](mailto:rudrakshrakeshzodage@gmail.com)  
- **GitHub**: [github.com/RudrakshRakeshZodage](https://github.com/RudrakshRakeshZodage/)  
- **LinkedIn**: [linkedin.com/in/rudraksh-zodage-](https://www.linkedin.com/in/rudraksh-zodage-/)  
- **HuggingFace**: [huggingface.co/rudrakshrakeshzodage](https://huggingface.co/rudrakshrakeshzodage)
