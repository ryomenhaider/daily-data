from src.collectors.crypto import fetch_crypto
from src.collectors.forex import fetch_forex
from src.collectors.macro import fetch_macro
from src.collectors.weather import fetch_weather

__all__ = [
    "fetch_crypto",
    "fetch_forex",
    "fetch_macro",
    "fetch_weather",
]