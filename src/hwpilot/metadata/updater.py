"""Metadata updater for hwpilot update command."""

import requests
import datetime
from typing import Tuple, Dict, Any, Optional
from hwpilot.metadata.store import load_metadata, save_metadata

OFFICIAL_METADATA_URL = "https://raw.githubusercontent.com/hwpilot/hwpilot/main/metadata/compatibility.json"


def update_metadata(timeout: int = 5) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Refreshes cached package compatibility metadata from official online sources.
    Returns (success, status_message, metadata_dict).
    """
    try:
        response = requests.get(OFFICIAL_METADATA_URL, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            data["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
            save_metadata(data)
            return True, "Successfully updated compatibility metadata from remote index.", data
        else:
            current = load_metadata()
            return False, f"Remote index returned HTTP {response.status_code}. Using cached/bundled metadata.", current
    except Exception as e:
        current = load_metadata()
        return False, f"Network error during metadata refresh ({str(e)}). Using cached/bundled metadata.", current
