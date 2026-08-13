from __future__ import annotations

from typing import Any

from .base import get_json


BASE_URL = "https://api.coinpaprika.com/v1"

COINS = {
    "btc-bitcoin": "bitcoin",
    "eth-ethereum": "ethereum",
    "sol-solana": "solana",
    "bnb-binance-coin": "bnb",
    "xrp-xrp": "xrp",
}


def fetch_crypto() -> dict[str, Any]:
    result: dict[str, Any] = {
        "source": "coinpaprika",
        "coins": {},
    }

    for coin_id, name in COINS.items():
        payload = get_json(f"{BASE_URL}/tickers/{coin_id}")

        result["coins"][name] = {
            "id": coin_id,
            "symbol": payload.get("symbol"),
            "name": payload.get("name"),
            "rank": payload.get("rank"),
            "price_usd": payload.get("quotes", {})
            .get("USD", {})
            .get("price"),
            "market_cap_usd": payload.get("quotes", {})
            .get("USD", {})
            .get("market_cap"),
            "volume_24h_usd": payload.get("quotes", {})
            .get("USD", {})
            .get("volume_24h"),
            "change_1h_pct": payload.get("quotes", {})
            .get("USD", {})
            .get("percent_change_1h"),
            "change_24h_pct": payload.get("quotes", {})
            .get("USD", {})
            .get("percent_change_24h"),
            "change_7d_pct": payload.get("quotes", {})
            .get("USD", {})
            .get("percent_change_7d"),
        }

    result["global"] = get_json(f"{BASE_URL}/global")

    return result