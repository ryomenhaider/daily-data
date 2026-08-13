from src.features.market import (
    crypto_features,
    forex_features,
    weather_features,
)


def test_crypto_features():

    data = {
        "coins": {
            "btc": {
                "symbol": "BTC",
                "market_cap_usd": 1000,
                "volume_24h_usd": 100,
                "change_24h_pct": 5,
                "change_7d_pct": 10,
            },
            "eth": {
                "symbol": "ETH",
                "market_cap_usd": 500,
                "volume_24h_usd": 50,
                "change_24h_pct": -2,
                "change_7d_pct": 3,
            },
        }
    }

    result = crypto_features(data)

    assert result["asset_count"] == 2
    assert result["total_market_cap_usd"] == 1500
    assert result["total_volume_24h_usd"] == 150
    assert result["best_24h_asset"] == "BTC"
    assert result["worst_24h_asset"] == "ETH"


def test_forex_features_dict():

    data = {
        "rates": {
            "EUR": 0.9,
            "GBP": 0.8,
            "JPY": 150,
        }
    }

    result = forex_features(data)

    assert result["currency_count"] == 3
    assert result["min_usd_rate"] == 0.8
    assert result["max_usd_rate"] == 150
    assert result["mean_usd_rate"] == (
        (0.9 + 0.8 + 150) / 3
    )


def test_forex_features_list():

    data = {
        "rates": [
            {
                "currency": "EUR",
                "rate": 0.9,
            },
            {
                "currency": "GBP",
                "rate": 0.8,
            },
            {
                "currency": "JPY",
                "rate": 150,
            },
        ]
    }

    result = forex_features(data)

    assert result["currency_count"] == 3
    assert result["min_usd_rate"] == 0.8
    assert result["max_usd_rate"] == 150


def test_weather_features():

    data = {
        "locations": {
            "A": {
                "temperature_c": 20,
            },
            "B": {
                "temperature_c": 30,
            },
        }
    }

    result = weather_features(data)

    assert result["location_count"] == 2
    assert result["mean_temperature_c"] == 25
    assert result["min_temperature_c"] == 20
    assert result["max_temperature_c"] == 30
