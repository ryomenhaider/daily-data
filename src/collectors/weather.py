from __future__ import annotations

from typing import Any

from .base import get_json


LOCATIONS = {
    "lahore": (31.5204, 74.3587),
    "islamabad": (33.6844, 73.0479),
    "karachi": (24.8607, 67.0011),
    "new_york": (40.7128, -74.0060),
}


def fetch_weather() -> dict[str, Any]:
    result: dict[str, Any] = {
        "source": "open-meteo",
        "locations": {},
    }

    for name, (latitude, longitude) in LOCATIONS.items():
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}"
            f"&longitude={longitude}"
            "&current=temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "wind_speed_10m"
            "&timezone=UTC"
        )

        payload = get_json(url)

        result["locations"][name] = {
            "latitude": latitude,
            "longitude": longitude,
            "current": payload.get("current", {}),
        }

    return result