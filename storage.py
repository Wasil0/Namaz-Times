"""Utilities for reading and writing saved prayer schedules."""

from __future__ import annotations

import json
import os
from typing import Any

SAVED_FILE = "saved_timings.json"


def load_saved_timings() -> list[dict[str, Any]]:
    """Return the saved schedule list or an empty list if no valid file exists."""
    if not os.path.exists(SAVED_FILE):
        return []

    try:
        with open(SAVED_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []
    return data


def save_timing_record(record: dict[str, Any]) -> None:
    """Append a record to the saved JSON file with pretty-print formatting."""
    existing_records = load_saved_timings()
    existing_records.append(record)

    with open(SAVED_FILE, "w", encoding="utf-8") as file:
        json.dump(existing_records, file, ensure_ascii=False, indent=2)
        file.write("\n")
