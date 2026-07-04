from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import requests
import yaml

VERDICT_AC = "AC"


def load_config(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    config.setdefault("server_url", "http://127.0.0.1:8000")
    config.setdefault("problems_dir", "./problems")
    config.setdefault("work_dir", "./tmp")
    config.setdefault("poll_interval", 3)
    config.setdefault("box_id", 0)
    if not config.get("name") or not config.get("key"):
        raise ValueError("Judge config must define both 'name' and 'key'.")
    return config


def read_problem(problems_dir: Path, problem_id: str) -> dict[str, Any]:
    problem_dir = problems_dir / problem_id
    meta_path = problem_dir / "problem.yml"
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing problem.yml for {problem_id}")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = yaml.safe_load(f) or {}
    meta["dir"] = problem_dir
    return meta


def testcase_pairs(problem: dict[str, Any]) -> list[tuple[Path, Path]]:
    problem_dir = Path(problem["dir"])
    tests_dir = problem_dir / "tests"
    pairs: list[tuple[Path, Path]] = []

    raw = problem.get("testcases") or []
    if isinstance(raw, dict):
        iterable = raw.items()
    else:
        iterable = []
        for item in raw:
            parts = str(item).split()
            if len(parts) == 2:
                iterable.append((parts[0], parts[1]))
    for inp, out in iterable:
        pairs.append((problem_dir / str(inp), problem_dir / str(out)))

    if not pairs and tests_dir.exists():
        for inp in sorted(tests_dir.glob("*.in")):
            out = inp.with_suffix(".out")
            if out.exists():
                pairs.append((inp, out))
    if not pairs:
        raise FileNotFoundError(f"No testcases found for {problem.get('id')}")
    return pairs


def compile_cpp(source: Path, output: Path) -> None:
    subprocess.run(
        ["g++", "-std=c++17", "-O2", "-pipe", "-static", "-s", str(source), "-o", str(output)],
        check=True,
        capture_output=True,
        text=True,
    )


def build_submission(task: dict[str, Any], work_dir: Path) -> Path:
    language = task["language"].lower()
    source = task["source_code"]
    if language not in {"cpp", "c++", "cc"}:
        raise ValueError(f"Unsupported language: {task['language']}")
    src = work_dir / "main.cpp"
    exe = work_dir / "main"
    src.write_text(source, encoding="utf-8")
    compile_cpp(src, exe)
    return exe


def run_process(exe: Path, input_path: Path, time_limit_ms: int, memory_limit_mb: int) -> dict[str, Any]:
    started = time.monotonic()
    with open(input_path, "rb") as fin:
        proc = subprocess.run(
            [str(exe)],
            stdin=fin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=max(time_limit_ms / 1000, 1),
        )
    elapsed = time.monotonic() - started
    verdict = VERDICT_AC if proc.returncode == 0 else "RE"
    return {"verdict": verdict, "output": proc.stdout, "stderr": proc.stderr.decode(errors="replace"), "time": elapsed, "memory": 0}


def normalize(data: bytes) -> str:
    return data.decode(errors="replace").strip().replace("\r\n", "\n")


def judge_task(task: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    work_dir = Path(config["work_dir"]) / str(task["submission_id"])
    shutil.rmtree(work_dir, ignore_errors=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    problem = read_problem(Path(config["problems_dir"]), task["problem_id"])
    exe = build_submission(task, work_dir)
    time_limit = int(problem.get("time_limit") or task.get("problem", {}).get("time_limit") or 2000)
    memory_limit = int(problem.get("memory_limit") or task.get("problem", {}).get("memory_limit") or 512)

    details = []
    max_time = 0.0
    max_memory = 0.0
    verdict = VERDICT_AC
    for index, (inp, expected) in enumerate(testcase_pairs(problem), start=1):
        try:
            run = run_process(exe, inp, time_limit, memory_limit)
        except subprocess.TimeoutExpired:
            run = {"verdict": "TLE", "output": b"", "stderr": "", "time": time_limit / 1000, "memory": 0}
        max_time = max(max_time, float(run["time"]))
        max_memory = max(max_memory, float(run["memory"]))
        expected_output = expected.read_bytes()
        if run["verdict"] != VERDICT_AC:
            verdict = run["verdict"]
        elif normalize(run["output"]) != normalize(expected_output):
            verdict = "WA"
            run["verdict"] = "WA"
        details.append({"test": index, "input": str(inp), "verdict": run["verdict"], "time": run["time"], "memory": run["memory"]})
        if verdict != VERDICT_AC:
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


def post(config: dict[str, Any], path: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = config["server_url"].rstrip("/") + path
    body = {"name": config["name"], "key": config["key"], **payload}
    response = requests.post(url, json=body, headers={"X-Judge-Key": config["key"]}, timeout=30)
    response.raise_for_status()
    return response.json()


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
                result = {"submission_id": task["submission_id"], "status": "Done", "verdict": "JE", "score": 0, "result": {"error": str(exc)}}
            post(config, "/api/judge/update-result", result)
        if args.once:
            break
        time.sleep(float(config["poll_interval"]))


if __name__ == "__main__":
    main()
