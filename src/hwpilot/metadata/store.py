"""Metadata storage and cache management."""

import json
from pathlib import Path
from typing import Dict, Any
import platformdirs

DEFAULTS_FILE = Path(__file__).parent / "defaults.json"


def get_cache_dir() -> Path:
    """Returns local user cache directory for HwPilot metadata."""
    cache_dir = Path(platformdirs.user_cache_dir("hwpilot", "hwpilot"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def load_metadata() -> Dict[str, Any]:
    """
    Loads compatibility metadata from local user cache if available,
    otherwise falls back to bundled defaults.json.
    """
    cache_file = get_cache_dir() / "compatibility_metadata.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Fallback to bundled defaults.json
    with open(DEFAULTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_metadata(data: Dict[str, Any]):
    """Saves updated compatibility metadata to user cache."""
    cache_file = get_cache_dir() / "compatibility_metadata.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
