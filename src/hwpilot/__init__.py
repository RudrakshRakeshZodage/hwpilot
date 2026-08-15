"""
HwPilot — Hardware-aware ML environment setup and compatibility manager.

Author: Rudraksh Rakesh Zodage
Email: rudrakshrakeshzodage@gmail.com
GitHub: https://github.com/RudrakshRakeshZodage/hwpilot
LinkedIn: https://www.linkedin.com/in/rudraksh-zodage-/
HuggingFace: https://huggingface.co/rudrakshrakeshzodage
"""

__version__ = "0.1.1"
__author__ = "Rudraksh Rakesh Zodage"
__email__ = "rudrakshrakeshzodage@gmail.com"

from hwpilot.models.hardware import SystemReport
from hwpilot.models.plan import InstallationPlan

__all__ = ["__version__", "__author__", "__email__", "SystemReport", "InstallationPlan"]
