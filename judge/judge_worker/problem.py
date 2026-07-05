from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def read_problem(problems_dir: Path, problem_id: str) -> dict[str, Any]:
    problem_dir = problems_dir / problem_id
    meta_path = problem_dir / "problem.yml"
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing problem.yml for {problem_id} in {problem_dir}")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = yaml.safe_load(f) or {}
    meta["id"] = meta.get("id", problem_id)
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

    missing = [str(path) for pair in pairs for path in pair if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing testcase file(s): " + ", ".join(missing))
    if not pairs:
        raise FileNotFoundError(f"No testcases found for {problem.get('id')}")
    return pairs
