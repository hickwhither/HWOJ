from __future__ import annotations

import yaml
import argparse
import time
from typing import Any

parser = argparse.ArgumentParser(description="EPenguinOJ judge worker")
parser.add_argument("--server_url", default="config.yml")
parser.add_argument("--poll_interval", action="store_true")
args = parser.parse_args()

# ONCE = args.once
SERVER_URL = args.server_url
POLL_INTERVAL = float(args.poll_interval)

with open("./config.yml", "r", encoding="utf-8") as f:
    judge_config = yaml.safe_load(f) or {}
    JUDGE_NAME = judge_config.get("name")
    JUDGE_KEY = judge_config.get("key")
    if not JUDGE_NAME or not JUDGE_KEY:
        raise ValueError("Judge config must define both 'name' and 'key'.")

from urllib.parse import urljoin
import requests
def post(path: str, payload: dict = None) -> dict[str, Any]:
    body = {"name": JUDGE_NAME, "key": JUDGE_KEY, **payload}
    response = requests.post(urljoin(SERVER_URL, path), json=body, timeout=30)
    response.raise_for_status()
    return response.json()

import importlib
languages = ["cpp14", "python3"]
lang_dict = {}
for i in languages:
    module = importlib.import_module(f"languages.{i}")
    lang_dict[i] = module.Executor

from core import judge_task
from isolate_runner import IsolateRunner
while True:
    task_response = post("/judge/get-task")
    task = task_response.get("task")
    if task:
        try:
            isolate = IsolateRunner()
            test_cases, err = judge_task(
                isolate=isolate,
                submission_id=task["submission_id"],
                problem_code=task["problem_code"],
                config=task["config"],
                language=lang_dict[task["language"]],
                source_code=task["source_code"],
            )
            total_time = 0
            total_memory = 0
            for i in test_cases:
                total_time += test_cases["time_used"]
                total_memory += test_cases["memory_used"]
            result = {
                "submission_id": task["submission_id"],
                "status": "D",
                "time_used": total_time,
                "memory_used": total_memory,
                "error": str(err),
                "test_cases": test_cases
            }
        except Exception as exc:
            result = {
                "submission_id": task["submission_id"],
                "status": "IE",
                "error": str(exc),
            }
        post("/api/judge/update-result", result)
    if args.once:
        break
    time.sleep(POLL_INTERVAL)


