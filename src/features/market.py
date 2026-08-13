from __future__ import annotations

import math
from statistics import mean
from typing import Any


def _numbers(values: list[Any]) -> list[float]:
    result = []

    for value in values:
        if value is None:
            continue

        try:
            value = float(value)

            if math.isfinite(value):
                result.append(value)

        except (TypeError, ValueError):
            continue

    return result


def crypto_features(crypto: dict[str, Any]) -> dict[str, Any]:
    coins = crypto["coins"]

    changes_24h = _numbers(
        [coin.get("change_24h_pct") for coin in coins.values()]
    )

    changes_7d = _numbers(
        [coin.get("change_7d_pct") for coin in coins.values()]
    )

    market_caps = _numbers(
        [coin.get("market_cap_usd") for coin in coins.values()]
    )

    volumes = _numbers(
        [coin.get("volume_24h_usd") for coin in coins.values()]
    )

    best = max(
        coins.values(),
        key=lambda x: x.get("change_24h_pct") or float("-inf"),
    )

    worst = min(
        coins.values(),
        key=lambda x: x.get("change_24h_pct") or float("inf"),
    )

    return {
        "asset_count": len(coins),
        "mean_change_24h_pct": mean(changes_24h)
        if changes_24h
        else None,
        "mean_change_7d_pct": mean(changes_7d)
        if changes_7d
        else None,
        "total_market_cap_usd": sum(market_caps),
        "total_volume_24h_usd": sum(volumes),
        "best_24h_asset": best.get("symbol"),
        "best_24h_change_pct": best.get("change_24h_pct"),
        "worst_24h_asset": worst.get("symbol"),
        "worst_24h_change_pct": worst.get("change_24h_pct"),
    }


def forex_features(forex: dict[str, Any]) -> dict[str, Any]:
    rates = forex.get("rates", {})

    values = _numbers(list(rates.values()))

    return {
        "currency_count": len(rates),
        "mean_usd_rate": mean(values) if values else None,
        "min_usd_rate": min(values) if values else None,
        "max_usd_rate": max(values) if values else None,
    }


def weather_features(weather: dict[str, Any]) -> dict[str, Any]:
    locations = weather.get("locations", {})

    temperatures = []

    for location in locations.values():
        current = location.get("current", {})
        value = current.get("temperature_2m")

        if value is not None:
            temperatures.append(float(value))

    return {
        "location_count": len(locations),
        "mean_temperature_c": mean(temperatures)
        if temperatures
        else None,
        "min_temperature_c": min(temperatures)
        if temperatures
        else None,
        "max_temperature_c": max(temperatures)
        if temperatures
        else None,
    }