from __future__ import annotations

import argparse
import time

from judge_worker.api import post
from judge_worker.config import load_config
from judge_worker.core import judge_task


def main() -> None:
    parser = argparse.ArgumentParser(description="EPenguinOJ judge worker")
    parser.add_argument("--config", default="config.yml")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)

    while True:
        task_response = post(config, "/api/judge/get-task", {})
        task = task_response.get("task")
        if task:
            try:
                result = judge_task(task, config)
            except Exception as exc:  # keep worker alive and report judge failure
                result = {
                    "submission_id": task["submission_id"],
                    "status": "Done",
                    "verdict": "JE",
                    "score": 0,
                    "result": {"error": str(exc)},
                }
            post(config, "/api/judge/update-result", result)
        if args.once:
            break
        time.sleep(float(config["poll_interval"]))


if __name__ == "__main__":
    main()
