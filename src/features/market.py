from __future__ import annotations

from math import isfinite
from statistics import mean
from typing import Any


def _number(value: Any, field: str) -> float:
    """Convert a value to a finite float."""
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid numeric value for '{field}': {value!r}"
        ) from exc

    if not isfinite(result):
        raise ValueError(
            f"Non-finite numeric value for '{field}': {value!r}"
        )

    return result


def _extract_rate_values(rates: Any) -> list[float]:
    """
    Normalize supported FX rate representations.

    Supported:

        {"EUR": 0.85, "GBP": 0.74}

    and:

        [{"currency": "EUR", "rate": 0.85}, ...]

    and:

        [{"code": "EUR", "value": 0.85}, ...]
    """

    if isinstance(rates, dict):
        values = []

        for currency, value in rates.items():
            values.append(
                _number(
                    value,
                    f"rates.{currency}",
                )
            )

        return values

    if isinstance(rates, list):
        values = []

        for index, item in enumerate(rates):

            if isinstance(item, (int, float)):
                values.append(
                    _number(
                        item,
                        f"rates[{index}]",
                    )
                )
                continue

            if not isinstance(item, dict):
                raise ValueError(
                    f"Invalid FX rate at index {index}: "
                    f"{item!r}"
                )

            value = (
                item.get("rate")
                if "rate" in item
                else item.get("value")
            )

            if value is None:
                raise ValueError(
                    f"FX rate at index {index} "
                    f"has no 'rate' or 'value': {item!r}"
                )

            values.append(
                _number(
                    value,
                    f"rates[{index}]",
                )
            )

        return values

    raise TypeError(
        "FX rates must be a dictionary or list, "
        f"got {type(rates).__name__}"
    )


def crypto_features(data: dict[str, Any]) -> dict[str, Any]:

    if not isinstance(data, dict):
        raise TypeError("Crypto data must be a dictionary.")

    coins_data = data.get("coins")

    if not isinstance(coins_data, dict):
        raise ValueError(
            "Crypto data must contain a 'coins' dictionary."
        )

    coins = list(coins_data.values())

    if not coins:
        raise ValueError(
            "Crypto dataset contains no assets."
        )

    changes_24h: list[float] = []

    total_market_cap = 0.0
    total_volume = 0.0

    normalized_coins = []

    for index, coin in enumerate(coins):

        if not isinstance(coin, dict):
            raise ValueError(
                f"Invalid crypto asset at index {index}."
            )

        symbol = str(
            coin.get("symbol", "UNKNOWN")
        )

        market_cap = _number(
            coin.get("market_cap_usd"),
            f"{symbol}.market_cap_usd",
        )

        volume = _number(
            coin.get("volume_24h_usd"),
            f"{symbol}.volume_24h_usd",
        )

        change = _number(
            coin.get("change_24h_pct"),
            f"{symbol}.change_24h_pct",
        )

        total_market_cap += market_cap
        total_volume += volume
        changes_24h.append(change)

        normalized_coins.append(
            {
                "symbol": symbol,
                "change_24h_pct": change,
            }
        )

    best = max(
        normalized_coins,
        key=lambda item: item["change_24h_pct"],
    )

    worst = min(
        normalized_coins,
        key=lambda item: item["change_24h_pct"],
    )

    return {
        "asset_count": len(coins),
        "total_market_cap_usd": total_market_cap,
        "total_volume_24h_usd": total_volume,
        "mean_change_24h_pct": mean(changes_24h),
        "best_24h_asset": best["symbol"],
        "best_24h_change_pct": best["change_24h_pct"],
        "worst_24h_asset": worst["symbol"],
        "worst_24h_change_pct": worst["change_24h_pct"],
    }


def forex_features(data: dict[str, Any]) -> dict[str, Any]:

    if not isinstance(data, dict):
        raise TypeError(
            "Forex data must be a dictionary."
        )

    if "rates" not in data:
        raise ValueError(
            "Forex data does not contain 'rates'."
        )

    rates = data["rates"]

    values = _extract_rate_values(rates)

    if not values:
        raise ValueError(
            "Forex dataset contains no rates."
        )

    return {
        "currency_count": len(values),
        "mean_usd_rate": mean(values),
        "min_usd_rate": min(values),
        "max_usd_rate": max(values),
    }


def weather_features(data: dict[str, Any]) -> dict[str, Any]:

    if not isinstance(data, dict):
        raise TypeError(
            "Weather data must be a dictionary."
        )

    locations = data.get("locations")

    if not isinstance(locations, dict):
        raise ValueError(
            "Weather data must contain a "
            "'locations' dictionary."
        )

    if not locations:
        raise ValueError(
            "Weather dataset contains no locations."
        )

    temperatures: list[float] = []

    for name, location in locations.items():

        if not isinstance(location, dict):
            raise ValueError(
                f"Invalid weather data for {name!r}."
            )

        temperatures.append(
            _number(
                location.get("temperature_c"),
                f"{name}.temperature_c",
            )
        )

    return {
        "location_count": len(temperatures),
        "mean_temperature_c": mean(temperatures),
        "min_temperature_c": min(temperatures),
        "max_temperature_c": max(temperatures),
        }
