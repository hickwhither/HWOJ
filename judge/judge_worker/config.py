from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_PROBLEMS_DIR = Path("/data/problems")


def load_config(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    config.setdefault("server_url", "http://127.0.0.1:8000")
    config.setdefault("problems_dir", str(DEFAULT_PROBLEMS_DIR))
    config.setdefault("work_dir", "./tmp")
    config.setdefault("poll_interval", 3)
    config.setdefault("box_id", 0)
    config.setdefault("use_cgroups", True)
    config.setdefault("compile_time_limit", 20)
    config.setdefault("wall_time_extra", 1.0)

    if not config.get("name") or not config.get("key"):
        raise ValueError("Judge config must define both 'name' and 'key'.")
    return config
