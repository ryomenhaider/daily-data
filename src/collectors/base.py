from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


USER_AGENT = "Rankistan-Daily-Pipeline/1.0"


class APIError(RuntimeError):
    pass


def get_json(
    url: str,
    *,
    retries: int = 3,
    timeout: int = 30,
) -> Any:
    last_error: Exception | None = None

    for attempt in range(retries):
        try:
            request = Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/json",
                },
            )

            with urlopen(request, timeout=timeout) as response:
                status = response.status
                body = response.read()

            if status >= 400:
                raise APIError(f"{url} returned HTTP {status}")

            return json.loads(body)

        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc

            if attempt < retries - 1:
                time.sleep(2 ** attempt)

    raise APIError(
        f"Failed to fetch {url} after {retries} attempts: {last_error}"
    )


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )