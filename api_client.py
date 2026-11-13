"""Live prayer time retrieval helpers for the Aladhan API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

CITY_URL = "https://api.aladhan.com/v1/timingsByCity"
COORDS_URL = "https://api.aladhan.com/v1/timings"


def _normalize_date(date_str: str | None) -> str:
    """Return the date in DD-MM-YYYY format or today's date."""
    if date_str and date_str.strip():
        return date_str.strip()
    return datetime.now().strftime("%d-%m-%Y")


def _request_data(url: str, params: dict[str, Any]) -> dict[str, Any] | None:
    """Perform a validated HTTP request and return the API data payload."""
    headers = {
        "Accept": "application/json",
        "User-Agent": "Namaz-Times-CLI/1.0",
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    try:
        payload = response.json()
    except ValueError:
        return None

    if payload.get("code") != 200:
        return None

    data = payload.get("data")
    return data if isinstance(data, dict) else None


def fetch_timings_by_city(
    city: str,
    country: str,
    date_str: str | None = None,
    method: int = 1,
    school: int = 1,
) -> dict | None:
    """Fetch today's or a custom-date prayer times by city and country."""
    if not city or not country:
        return None

    normalized_date = _normalize_date(date_str)
    url = f"{CITY_URL}/{normalized_date}"
    params = {
        "city": city,
        "country": country,
        "method": method,
        "school": school,
    }
    return _request_data(url, params)


def fetch_timings_by_coords(
    latitude: float,
    longitude: float,
    date_str: str | None = None,
    method: int = 3,
    school: int = 0,
) -> dict | None:
    """Fetch prayer timings based on latitude and longitude."""
    normalized_date = _normalize_date(date_str)
    url = f"{COORDS_URL}/{normalized_date}"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "method": method,
        "school": school,
    }
    return _request_data(url, params)
