"""Logging setup for HwPilot."""

import logging
import os
from pathlib import Path

_logger: logging.Logger = None


def setup_logger(log_dir: str = "./logs", verbose: bool = False) -> logging.Logger:
    global _logger
    _logger = logging.getLogger("hwpilot")
    _logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Avoid duplicate handlers
    if _logger.handlers:
        return _logger

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    )

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if verbose else logging.WARNING)
    ch.setFormatter(formatter)
    _logger.addHandler(ch)

    # File handler
    try:
        p = Path(log_dir)
        p.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(p / "hwpilot.log", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        _logger.addHandler(fh)
    except Exception:
        pass

    return _logger


def get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        return setup_logger()
    return _logger
