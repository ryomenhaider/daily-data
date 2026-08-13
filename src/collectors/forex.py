from __future__ import annotations

from typing import Any

from .base import get_json


BASE_URL = "https://api.frankfurter.dev/v2"


def fetch_forex() -> dict[str, Any]:
    payload = get_json(
        f"{BASE_URL}/rates"
        "?base=USD"
        "&quotes=EUR,GBP,JPY,CNY,PKR,AUD,CAD,CHF"
    )

    return {
        "source": "frankfurter",
        "base": "USD",
        "rates": payload,
    }
