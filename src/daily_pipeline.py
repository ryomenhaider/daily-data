from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.collectors import (
    fetch_crypto,
    fetch_forex,
    fetch_macro,
    fetch_weather,
)

from src.features import (
    crypto_features,
    forex_features,
    weather_features,
)


ROOT = Path(__file__).resolve().parents[1]

NOW = datetime.now(timezone.utc)

DATE = NOW.strftime("%Y-%m-%d")
RUN_ID = NOW.strftime("%Y-%m-%d-%H-%M-%S")

DATA_DIR = (
    ROOT
    / "data"
    / NOW.strftime("%Y")
    / NOW.strftime("%m")
    / NOW.strftime("%d")
    / RUN_ID
)

RAW_DIR = DATA_DIR / "raw"
FEATURE_DIR = DATA_DIR / "features"

REPORT_DIR = (
    ROOT
    / "reports"
    / NOW.strftime("%Y")
    / NOW.strftime("%m")
    / NOW.strftime("%d")
)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def commit(message: str, path: Path) -> None:
    import subprocess

    relative = str(path.relative_to(ROOT))

    subprocess.run(
        ["git", "add", relative],
        cwd=ROOT,
        check=True,
    )

    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=ROOT,
    )

    if result.returncode == 0:
        raise RuntimeError(
            f"Refusing empty commit: {message}"
        )

    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=ROOT,
        check=True,
    )


def generate_report(
    crypto: dict,
    forex: dict,
    weather: dict,
    macro: dict,
    crypto_stats: dict,
    forex_stats: dict,
    weather_stats: dict,
) -> Path:

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = REPORT_DIR / f"{RUN_ID}.md"

    lines = [
        f"# Intelligence Report — {RUN_ID}",
        "",
        f"Generated: `{NOW.isoformat()}`",
        "",
        "## Cryptocurrency",
        "",
        f"- Assets: {crypto_stats['asset_count']}",
        f"- Total market cap: ${crypto_stats['total_market_cap_usd']:,.0f}",
        f"- Total volume: ${crypto_stats['total_volume_24h_usd']:,.0f}",
        f"- Mean 24h change: {crypto_stats['mean_change_24h_pct']:.2f}%",
        f"- Best performer: {crypto_stats['best_24h_asset']}",
        f"- Worst performer: {crypto_stats['worst_24h_asset']}",
        "",
        "## Forex",
        "",
        f"- Currencies: {forex_stats['currency_count']}",
        f"- Mean USD rate: {forex_stats['mean_usd_rate']:.4f}",
        f"- Minimum USD rate: {forex_stats['min_usd_rate']:.4f}",
        f"- Maximum USD rate: {forex_stats['max_usd_rate']:.4f}",
        "",
        "## Weather",
        "",
        f"- Locations: {weather_stats['location_count']}",
        f"- Mean temperature: {weather_stats['mean_temperature_c']:.2f} °C",
        f"- Minimum temperature: {weather_stats['min_temperature_c']:.2f} °C",
        f"- Maximum temperature: {weather_stats['max_temperature_c']:.2f} °C",
        "",
        "## Macroeconomics",
        "",
    ]

    for country, indicators in macro.get(
        "countries",
        {},
    ).items():

        lines.append(f"### {country}")
        lines.append("")

        for name, value in indicators.items():

            if isinstance(value, dict):

                lines.append(
                    f"- **{name}**: "
                    f"{value.get('value')} "
                    f"({value.get('year')})"
                )

            else:

                lines.append(
                    f"- **{name}**: {value}"
                )

        lines.append("")

    lines.extend(
        [
            "## Sources",
            "",
            "- CoinPaprika",
            "- Frankfurter",
            "- Open-Meteo",
            "- World Bank",
            "",
            f"Run ID: `{RUN_ID}`",
        ]
    )

    path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    return path


def main() -> None:

    print("=" * 70)
    print("DAILY INTELLIGENCE PIPELINE")
    print("=" * 70)

    print(f"RUN ID: {RUN_ID}")
    print(f"DATA:   {DATA_DIR}")

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    FEATURE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # 1. Crypto
    crypto = fetch_crypto()

    crypto_path = RAW_DIR / "crypto.json"

    write_json(
        crypto_path,
        crypto,
    )

    commit(
        f"data: add crypto snapshot {RUN_ID}",
        crypto_path,
    )

    # 2. Forex
    forex = fetch_forex()

    forex_path = RAW_DIR / "forex.json"

    write_json(
        forex_path,
        forex,
    )

    commit(
        f"data: add forex snapshot {RUN_ID}",
        forex_path,
    )

    # 3. Weather
    weather = fetch_weather()

    weather_path = RAW_DIR / "weather.json"

    write_json(
        weather_path,
        weather,
    )

    commit(
        f"data: add weather snapshot {RUN_ID}",
        weather_path,
    )

    # 4. Macro
    macro = fetch_macro()

    macro_path = RAW_DIR / "macro.json"

    write_json(
        macro_path,
        macro,
    )

    commit(
        f"data: add macro snapshot {RUN_ID}",
        macro_path,
    )

    # 5. Crypto features
    crypto_stats = crypto_features(crypto)

    crypto_feature_path = (
        FEATURE_DIR / "crypto.json"
    )

    write_json(
        crypto_feature_path,
        crypto_stats,
    )

    commit(
        f"feat: engineer crypto features {RUN_ID}",
        crypto_feature_path,
    )

    # 6. Forex features
    forex_stats = forex_features(forex)

    forex_feature_path = (
        FEATURE_DIR / "forex.json"
    )

    write_json(
        forex_feature_path,
        forex_stats,
    )

    commit(
        f"feat: engineer forex features {RUN_ID}",
        forex_feature_path,
    )

    # 7. Weather features
    weather_stats = weather_features(weather)

    weather_feature_path = (
        FEATURE_DIR / "weather.json"
    )

    write_json(
        weather_feature_path,
        weather_stats,
    )

    commit(
        f"feat: engineer weather features {RUN_ID}",
        weather_feature_path,
    )

    # 8. Combined features
    combined = {
        "run_id": RUN_ID,
        "timestamp": NOW.isoformat(),
        "crypto": crypto_stats,
        "forex": forex_stats,
        "weather": weather_stats,
    }

    combined_path = (
        FEATURE_DIR / "daily.json"
    )

    write_json(
        combined_path,
        combined,
    )

    commit(
        f"feat: add combined feature set {RUN_ID}",
        combined_path,
    )

    # 9. Report
    report_path = generate_report(
        crypto,
        forex,
        weather,
        macro,
        crypto_stats,
        forex_stats,
        weather_stats,
    )

    commit(
        f"docs: publish intelligence report {RUN_ID}",
        report_path,
    )

    # 10. Metadata
    metadata = {
        "run_id": RUN_ID,
        "timestamp": NOW.isoformat(),
        "date": DATE,
        "status": "success",
        "sources": [
            "coinpaprika",
            "frankfurter",
            "open-meteo",
            "world-bank",
        ],
    }

    metadata_path = DATA_DIR / "run.json"

    write_json(
        metadata_path,
        metadata,
    )

    commit(
        f"chore: record pipeline run {RUN_ID}",
        metadata_path,
    )

    print()
    print("=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()