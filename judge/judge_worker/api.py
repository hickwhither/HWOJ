from __future__ import annotations

from typing import Any

import requests


def post(config: dict[str, Any], path: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = config["server_url"].rstrip("/") + path
    body = {"name": config["name"], "key": config["key"], **payload}
    response = requests.post(url, json=body, headers={"X-Judge-Key": config["key"]}, timeout=30)
    response.raise_for_status()
    return response.json()
