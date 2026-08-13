from __future__ import annotations

from typing import Any

import requests


URL = "https://api.frankfurter.app/latest"

CURRENCIES = [
    "GBP",
    "EUR",
    "JPY",
    "CHF",
    "CAD",
    "AUD",
    "CNY",
    "INR",
    "PKR",
    "AED",
    "SAR",
    "TRY",
]


def _validate_rates(
    rates: Any,
) -> dict[str, float]:

    if not isinstance(rates, dict):
        raise ValueError(
            "Frankfurter returned invalid rates: "
            f"expected dict, got {type(rates).__name__}"
        )

    normalized: dict[str, float] = {}

    for currency, value in rates.items():

        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid FX rate for {currency}: {value!r}"
            ) from exc

        if not isinstance(currency, str):
            raise ValueError(
                f"Invalid currency code: {currency!r}"
            )

        normalized[currency] = numeric

    if not normalized:
        raise ValueError(
            "Frankfurter returned an empty rates object."
        )

    return normalized


def fetch_forex() -> dict[str, Any]:

    response = requests.get(
        URL,
        params={
            "from": "USD",
            "to": ",".join(CURRENCIES),
        },
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()

    if not isinstance(payload, dict):
        raise ValueError(
            "Frankfurter response must be a JSON object."
        )

    base = payload.get("base")

    if not isinstance(base, str):
        raise ValueError(
            "Frankfurter response missing valid 'base'."
        )

    date = payload.get("date")

    if not isinstance(date, str):
        raise ValueError(
            "Frankfurter response missing valid 'date'."
        )

    rates = _validate_rates(
        payload.get("rates")
    )

    return {
        "source": "frankfurter",
        "base": base,
        "date": date,
        "rates": rates,
        }
