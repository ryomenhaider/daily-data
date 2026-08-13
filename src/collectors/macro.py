from __future__ import annotations

from typing import Any

from .base import get_json


COUNTRIES = {
    "PAK": "PAK",
    "USA": "USA",
    "CHN": "CHN",
}

INDICATORS = {
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "inflation": "FP.CPI.TOTL.ZG",
    "unemployment": "SL.UEM.TOTL.ZS",
}


def fetch_indicator(
    country: str,
    indicator: str,
) -> dict[str, Any]:
    url = (
        f"https://api.worldbank.org/v2/country/"
        f"{country}/indicator/{indicator}"
        "?format=json&per_page=5"
    )

    payload = get_json(url)

    if not isinstance(payload, list) or len(payload) < 2:
        return {
            "country": country,
            "indicator": indicator,
            "value": None,
            "year": None,
        }

    records = payload[1]

    for record in records:
        if record.get("value") is not None:
            return {
                "country": country,
                "indicator": indicator,
                "value": record.get("value"),
                "year": record.get("date"),
            }

    return {
        "country": country,
        "indicator": indicator,
        "value": None,
        "year": None,
    }


def fetch_macro() -> dict[str, Any]:
    result: dict[str, Any] = {
        "source": "world-bank",
        "countries": {},
    }

    for country in COUNTRIES:
        result["countries"][country] = {}

        for name, indicator in INDICATORS.items():
            result["countries"][country][name] = fetch_indicator(
                country,
                indicator,
            )

    return result