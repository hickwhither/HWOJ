from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .build import build_submission
from .isolate_runner import IsolateConfig, IsolateRunner, VERDICT_AC
from .problem import read_problem, testcase_pairs


def normalize(data: bytes) -> str:
    return data.decode(errors="replace").strip().replace("\r\n", "\n")


def judge_task(task: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    work_dir = Path(config["work_dir"]) / str(task["submission_id"])
    shutil.rmtree(work_dir, ignore_errors=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    problem = read_problem(Path(config["problems_dir"]), task["problem_id"])
    executable = build_submission(task, work_dir, float(config.get("compile_time_limit", 20)))
    time_limit = int(problem.get("time_limit") or task.get("problem", {}).get("time_limit") or 2000)
    memory_limit = int(problem.get("memory_limit") or task.get("problem", {}).get("memory_limit") or 512)

    details: list[dict[str, Any]] = []
    max_time = 0.0
    max_memory = 0.0
    verdict = VERDICT_AC

    isolate_config = IsolateConfig(
        box_id=int(config.get("box_id", 0)),
        use_cgroups=bool(config.get("use_cgroups", True)),
        wall_time_extra=float(config.get("wall_time_extra", 1.0)),
    )
    with IsolateRunner(isolate_config) as runner:
        for index, (inp, expected) in enumerate(testcase_pairs(problem), start=1):
            run = runner.run(executable, inp, time_limit, memory_limit)
            max_time = max(max_time, float(run["time"]))
            max_memory = max(max_memory, float(run["memory"]))

            test_verdict = run["verdict"]
            if test_verdict == VERDICT_AC and normalize(run["output"]) != normalize(expected.read_bytes()):
                test_verdict = "WA"

            details.append(
                {
                    "test": index,
                    "input": str(inp),
                    "verdict": test_verdict,
                    "time": run["time"],
                    "memory": run["memory"],
                }
            )
            if test_verdict != VERDICT_AC:
                verdict = test_verdict
                break

    return {
        "submission_id": task["submission_id"],
        "status": "Done",
        "verdict": verdict,
        "score": 100 if verdict == VERDICT_AC else 0,
        "time_used": max_time,
        "memory_used": max_memory,
        "result": {"tests": details},
    }
