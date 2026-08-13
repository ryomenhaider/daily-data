from __future__ import annotations

import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from collectors import (
    fetch_crypto,
    fetch_forex,
    fetch_macro,
    fetch_weather,
)

from features import (
    crypto_features,
    forex_features,
    weather_features,
)


ROOT = Path(__file__).resolve().parents[1]

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
TIMESTAMP = datetime.now(timezone.utc).isoformat()

DATA_DIR = ROOT / "data" / TODAY
REPORT_DIR = ROOT / "reports"

RAW_DIR = DATA_DIR / "raw"
FEATURE_DIR = DATA_DIR / "features"


def run(command: list[str]) -> str:
    print("$", " ".join(command))

    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(
            f"Command failed: {' '.join(command)}"
        )

    return result.stdout.strip()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )


def commit(message: str, paths: list[str]) -> None:
    run(["git", "add", *paths])

    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=ROOT,
    )

    if result.returncode == 0:
        print(f"Skipping empty stage: {message}")
        return

    run(["git", "commit", "-m", message])


def validate_json(path: Path) -> None:
    with path.open(encoding="utf-8") as file:
        json.load(file)


def generate_report(
    crypto: dict[str, Any],
    forex: dict[str, Any],
    weather: dict[str, Any],
    macro: dict[str, Any],
    crypto_stats: dict[str, Any],
    forex_stats: dict[str, Any],
    weather_stats: dict[str, Any],
) -> Path:

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    path = REPORT_DIR / f"{TODAY}.md"

    lines = [
        f"# Daily Intelligence Report — {TODAY}",
        "",
        f"Generated: `{TIMESTAMP}`",
        "",
        "## Cryptocurrency",
        "",
        f"- Assets tracked: {crypto_stats['asset_count']}",
        (
            f"- Combined market cap: "
            f"${crypto_stats['total_market_cap_usd']:,.0f}"
        ),
        (
            f"- 24h volume: "
            f"${crypto_stats['total_volume_24h_usd']:,.0f}"
        ),
        (
            f"- Mean 24h change: "
            f"{crypto_stats['mean_change_24h_pct']:.2f}%"
        ),
        (
            f"- Best performer: "
            f"{crypto_stats['best_24h_asset']} "
            f"({crypto_stats['best_24h_change_pct']:.2f}%)"
        ),
        (
            f"- Worst performer: "
            f"{crypto_stats['worst_24h_asset']} "
            f"({crypto_stats['worst_24h_change_pct']:.2f}%)"
        ),
        "",
        "### Assets",
        "",
        "| Asset | Price | Market Cap | 24h | 7d |",
        "|---|---:|---:|---:|---:|",
    ]

    for coin in crypto["coins"].values():
        lines.append(
            "| "
            f"{coin['symbol']} | "
            f"${coin['price_usd']:,.6f} | "
            f"${coin['market_cap_usd']:,.0f} | "
            f"{coin['change_24h_pct']:.2f}% | "
            f"{coin['change_7d_pct']:.2f}% |"
        )

    lines += [
        "",
        "## Foreign Exchange",
        "",
        f"- Currencies: {forex_stats['currency_count']}",
        f"- Mean USD rate: {forex_stats['mean_usd_rate']:.4f}",
        f"- Minimum rate: {forex_stats['min_usd_rate']:.4f}",
        f"- Maximum rate: {forex_stats['max_usd_rate']:.4f}",
        "",
        "## Weather",
        "",
        f"- Locations: {weather_stats['location_count']}",
        (
            f"- Mean temperature: "
            f"{weather_stats['mean_temperature_c']:.2f} °C"
        ),
        (
            f"- Minimum temperature: "
            f"{weather_stats['min_temperature_c']:.2f} °C"
        ),
        (
            f"- Maximum temperature: "
            f"{weather_stats['max_temperature_c']:.2f} °C"
        ),
        "",
        "## Macroeconomics",
        "",
    ]

    for country, indicators in macro["countries"].items():
        lines.append(f"### {country}")
        lines.append("")

        for name, value in indicators.items():
            lines.append(
                f"- **{name}**: "
                f"{value.get('value')} "
                f"({value.get('year')})"
            )

        lines.append("")

    lines += [
        "## Data Sources",
        "",
        "- CoinPaprika",
        "- Frankfurter",
        "- Open-Meteo",
        "- World Bank",
        "",
        "This report is generated automatically by the daily pipeline.",
    ]

    path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    return path


def main() -> None:
    print("=" * 60)
    print(f"Daily Pipeline — {TODAY}")
    print("=" * 60)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    FEATURE_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Crypto
    # ------------------------------------------------------------------

    print("\n[1/10] Collecting cryptocurrency data")

    crypto = fetch_crypto()

    crypto_path = RAW_DIR / "crypto.json"

    write_json(crypto_path, crypto)
    validate_json(crypto_path)

    commit(
        f"data: add crypto snapshot for {TODAY}",
        [str(crypto_path.relative_to(ROOT))],
    )

    # ------------------------------------------------------------------
    # 2. Forex
    # ------------------------------------------------------------------

    print("\n[2/10] Collecting FX data")

    forex = fetch_forex()

    forex_path = RAW_DIR / "forex.json"

    write_json(forex_path, forex)
    validate_json(forex_path)

    commit(
        f"data: add forex snapshot for {TODAY}",
        [str(forex_path.relative_to(ROOT))],
    )

    # ------------------------------------------------------------------
    # 3. Weather
    # ------------------------------------------------------------------

    print("\n[3/10] Collecting weather data")

    weather = fetch_weather()

    weather_path = RAW_DIR / "weather.json"

    write_json(weather_path, weather)
    validate_json(weather_path)

    commit(
        f"data: add weather snapshot for {TODAY}",
        [str(weather_path.relative_to(ROOT))],
    )

    # ------------------------------------------------------------------
    # 4. Macro
    # ------------------------------------------------------------------

    print("\n[4/10] Collecting macroeconomic data")

    macro = fetch_macro()

    macro_path = RAW_DIR / "macro.json"

    write_json(macro_path, macro)
    validate_json(macro_path)

    commit(
        f"data: add macro snapshot for {TODAY}",
        [str(macro_path.relative_to(ROOT))],
    )

    # ------------------------------------------------------------------
    # 5. Crypto features
    # ------------------------------------------------------------------

    print("\n[5/10] Engineering crypto features")

    crypto_stats = crypto_features(crypto)

    crypto_feature_path = FEATURE_DIR / "crypto.json"

    write_json(
        crypto_feature_path,
        crypto_stats,
    )

    commit(
        f"feat: engineer crypto features for {TODAY}",
        [str(crypto_feature_path.relative_to(ROOT))],
    )

    # ------------------------------------------------------------------
    # 6. FX features
    # ------------------------------------------------------------------

    print("\n[6/10] Engineering FX features")

    forex_stats = forex_features(forex)

    forex_feature_path = FEATURE_DIR / "forex.json"

    write_json(
        forex_feature_path,
        forex_stats,
    )

    commit(
        f"feat: engineer forex features for {TODAY}",
        [str(forex_feature_path.relative_to(ROOT))],
    )

    # ------------------------------------------------------------------
    # 7. Weather features
    # ------------------------------------------------------------------

    print("\n[7/10] Engineering weather features")

    weather_stats = weather_features(weather)

    weather_feature_path = FEATURE_DIR / "weather.json"

    write_json(
        weather_feature_path,
        weather_stats,
    )

    commit(
        f"feat: engineer weather features for {TODAY}",
        [str(weather_feature_path.relative_to(ROOT))],
    )

    # ------------------------------------------------------------------
    # 8. Combined feature dataset
    # ------------------------------------------------------------------

    print("\n[8/10] Building combined feature dataset")

    combined = {
        "date": TODAY,
        "crypto": crypto_stats,
        "forex": forex_stats,
        "weather": weather_stats,
    }

    combined_path = FEATURE_DIR / "daily.json"

    write_json(combined_path, combined)

    commit(
        f"feat: add combined daily feature set for {TODAY}",
        [str(combined_path.relative_to(ROOT))],
    )

    # ------------------------------------------------------------------
    # 9. Report
    # ------------------------------------------------------------------

    print("\n[9/10] Generating intelligence report")

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
        f"docs: publish daily intelligence report for {TODAY}",
        [str(report_path.relative_to(ROOT))],
    )
    print("\n[10/10] Writing pipeline metadata")

    metadata = {
        "date": TODAY,
        "generated_at": TIMESTAMP,
        "sources": [
            "coinpaprika",
            "frankfurter",
            "open-meteo",
            "world-bank",
        ],
        "status": "success",
    }

    metadata_path = DATA_DIR / "run.json"

    write_json(metadata_path, metadata)

    commit(
        f"chore: record pipeline run for {TODAY}",
        [str(metadata_path.relative_to(ROOT))],
    )

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()