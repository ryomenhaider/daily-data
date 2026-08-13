from .crypto import fetch_crypto
from .forex import fetch_forex
from .macro import fetch_macro
from .weather import fetch_weather

__all__ = [
    "fetch_crypto",
    "fetch_forex",
    "fetch_macro",
    "fetch_weather",
]