from __future__ import annotations

import requests


URL = "https://api.coinpaprika.com/v1/tickers"

COINS = {
    "btc-bitcoin",
    "eth-ethereum",
    "sol-solana",
    "bnb-binance-coin",
    "xrp-xrp",
    "ada-cardano",
    "doge-dogecoin",
    "avax-avalanche",
    "dot-polkadot",
    "link-chainlink",
}


def fetch_crypto() -> dict:

    response = requests.get(
        URL,
        params={
            "quotes": "USD",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    selected = {}

    for coin in data:

        if coin["id"] not in COINS:
            continue

        usd = coin["quotes"]["USD"]

        selected[coin["id"]] = {
            "id": coin["id"],
            "name": coin["name"],
            "symbol": coin["symbol"],
            "rank": coin["rank"],
            "price_usd": usd["price"],
            "market_cap_usd": usd["market_cap"],
            "volume_24h_usd": usd["volume_24h"],
            "change_24h_pct": usd["percent_change_24h"],
            "change_7d_pct": usd["percent_change_7d"],
        }

    if not selected:
        raise RuntimeError(
            "Crypto API returned no selected assets"
        )

    return {
        "source": "coinpaprika",
        "coins": selected,
    }