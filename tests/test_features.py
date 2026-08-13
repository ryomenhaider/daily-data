from src.features.market import (
    crypto_features,
    forex_features,
    weather_features,
)


def test_crypto_features():
    data = {
        "coins": {
            "bitcoin": {
                "symbol": "BTC",
                "price_usd": 100,
                "market_cap_usd": 1_000,
                "volume_24h_usd": 100,
                "change_24h_pct": 5,
                "change_7d_pct": 10,
            },
            "ethereum": {
                "symbol": "ETH",
                "price_usd": 50,
                "market_cap_usd": 500,
                "volume_24h_usd": 50,
                "change_24h_pct": -1,
                "change_7d_pct": 2,
            },
        }
    }

    result = crypto_features(data)

    assert result["asset_count"] == 2
    assert result["best_24h_asset"] == "BTC"
    assert result["worst_24h_asset"] == "ETH"
    assert result["total_market_cap_usd"] == 1500


def test_forex_features():
    data = {
        "rates": {
            "EUR": 0.85,
            "GBP": 0.74,
            "PKR": 280,
        }
    }

    result = forex_features(data)

    assert result["currency_count"] == 3
    assert result["min_usd_rate"] == 0.74


def test_weather_features():
    data = {
        "locations": {
            "lahore": {
                "current": {
                    "temperature_2m": 30,
                }
            },
            "islamabad": {
                "current": {
                    "temperature_2m": 25,
                }
            },
        }
    }

    result = weather_features(data)

    assert result["location_count"] == 2
    assert result["mean_temperature_c"] == 27.5