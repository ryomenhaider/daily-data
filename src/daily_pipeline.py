from __future__ import annotations

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

NOW = datetime.now(timezone.utc)

DATE = NOW.strftime("%Y-%m-%d")
RUN_ID = NOW.strftime("%Y-%m-%d-%H-%M-%S")

DATA_DIR = ROOT / "data" / NOW.strftime("%Y") / NOW.strftime("%m") / NOW.strftime("%d") / RUN_ID

RAW_DIR = DATA_DIR / "raw"
FEATURE_DIR = DATA_DIR / "features"

REPORT_DIR = ROOT / "reports" / NOW.strftime("%Y") / NOW.strftime("%m") / NOW.strftime("%d")


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
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )


def commit(
    message: str,
    paths: list[str],
) -> None:

    run([
        "git",
        "add",
        *paths,
    ])

    result = subprocess.run(
        [
            "git",
            "diff",
            "--cached",
            "--quiet",
        ],
        cwd=ROOT,
    )

    # No staged changes.
    if result.returncode == 0:
        print(
            f"Skipping empty commit: {message}"
        )
        return

    run([
        "git",
        "commit",
        "-m",
        message,
    ])


def validate_json(path: Path) -> None:
    with path.open(
        encoding="utf-8"
    ) as file:
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

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        REPORT_DIR /
        f"{RUN_ID}.md"
    )

    lines = [
        f"# Intelligence Report — {RUN_ID}",
        "",
        f"Generated: `{NOW.isoformat()}`",
        "",
        "## Cryptocurrency",
        "",
        f"- Assets tracked: {crypto_stats['asset_count']}",
        (
            f"- Combined market cap: "
            f"${crypto_stats['total_market_cap_usd']:,.0f}"
        ),
        (
            f"- Combined 24h volume: "
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

        lines.append(
            f"### {country}"
        )

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
        f"Run ID: `{RUN_ID}`",
    ]

    path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    return path


def main() -> None:

    print("=" * 70)
    print("DAILY INTELLIGENCE PIPELINE")
    print("=" * 70)

    print(f"Date:   {DATE}")
    print(f"Run ID: {RUN_ID}")
    print(f"Data:   {DATA_DIR}")

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    FEATURE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ================================================================
    # 1. CRYPTO
    # ================================================================

    print("\n[1/10] Cryptocurrency")

    crypto = fetch_crypto()

    crypto_path = (
        RAW_DIR /
        "crypto.json"
    )

    write_json(
        crypto_path,
        crypto,
    )

    validate_json(
        crypto_path
    )

    commit(
        f"data: add crypto snapshot {RUN_ID}",
        [
            str(
                crypto_path.relative_to(ROOT)
            )
        ],
    )

    # ================================================================
    # 2. FOREX
    # ================================================================

    print("\n[2/10] Foreign exchange")

    forex = fetch_forex()

    forex_path = (
        RAW_DIR /
        "forex.json"
    )

    write_json(
        forex_path,
        forex,
    )

    validate_json(
        forex_path
    )

    commit(
        f"data: add forex snapshot {RUN_ID}",
        [
            str(
                forex_path.relative_to(ROOT)
            )
        ],
    )

    # ================================================================
    # 3. WEATHER
    # ================================================================

    print("\n[3/10] Weather")

    weather = fetch_weather()

    weather_path = (
        RAW_DIR /
        "weather.json"
    )

    write_json(
        weather_path,
        weather,
    )

    validate_json(
        weather_path
    )

    commit(
        f"data: add weather snapshot {RUN_ID}",
        [
            str(
                weather_path.relative_to(ROOT)
            )
        ],
    )

    # ================================================================
    # 4. MACRO
    # ================================================================

    print("\n[4/10] Macroeconomics")

    macro = fetch_macro()

    macro_path = (
        RAW_DIR /
        "macro.json"
    )

    write_json(
        macro_path,
        macro,
    )

    validate_json(
        macro_path
    )

    commit(
        f"data: add macro snapshot {RUN_ID}",
        [
            str(
                macro_path.relative_to(ROOT)
            )
        ],
    )

    # ================================================================
    # 5. CRYPTO FEATURES
    # ================================================================

    print("\n[5/10] Crypto features")

    crypto_stats = crypto_features(
        crypto
    )

    crypto_feature_path = (
        FEATURE_DIR /
        "crypto.json"
    )

    write_json(
        crypto_feature_path,
        crypto_stats,
    )

    commit(
        f"feat: engineer crypto features {RUN_ID}",
        [
            str(
                crypto_feature_path.relative_to(ROOT)
            )
        ],
    )

    # ================================================================
    # 6. FOREX FEATURES
    # ================================================================

    print("\n[6/10] Forex features")

    forex_stats = forex_features(
        forex
    )

    forex_feature_path = (
        FEATURE_DIR /
        "forex.json"
    )

    write_json(
        forex_feature_path,
        forex_stats,
    )

    commit(
        f"feat: engineer forex features {RUN_ID}",
        [
            str(
                forex_feature_path.relative_to(ROOT)
            )
        ],
    )

    # ================================================================
    # 7. WEATHER FEATURES
    # ================================================================

    print("\n[7/10] Weather features")

    weather_stats = weather_features(
        weather
    )

    weather_feature_path = (
        FEATURE_DIR /
        "weather.json"
    )

    write_json(
        weather_feature_path,
        weather_stats,
    )

    commit(
        f"feat: engineer weather features {RUN_ID}",
        [
            str(
                weather_feature_path.relative_to(ROOT)
            )
        ],
    )

    # ================================================================
    # 8. COMBINED FEATURES
    # ================================================================

    print("\n[8/10] Combined feature set")

    combined = {
        "run_id": RUN_ID,
        "timestamp": NOW.isoformat(),
        "crypto": crypto_stats,
        "forex": forex_stats,
        "weather": weather_stats,
    }

    combined_path = (
        FEATURE_DIR /
        "daily.json"
    )

    write_json(
        combined_path,
        combined,
    )

    commit(
        f"feat: add combined feature set {RUN_ID}",
        [
            str(
                combined_path.relative_to(ROOT)
            )
        ],
    )

    # ================================================================
    # 9. REPORT
    # ================================================================

    print("\n[9/10] Intelligence report")

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
        [
            str(
                report_path.relative_to(ROOT)
            )
        ],
    )

    # ================================================================
    # 10. METADATA
    # ================================================================

    print("\n[10/10] Pipeline metadata")

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

    metadata_path = (
        DATA_DIR /
        "run.json"
    )

    write_json(
        metadata_path,
        metadata,
    )

    commit(
        f"chore: record pipeline run {RUN_ID}",
        [
            str(
                metadata_path.relative_to(ROOT)
            )
        ],
    )

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()