from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def compile_cpp(source: Path, output: Path, timeout: float = 20) -> None:
    subprocess.run(
        ["g++", "-std=c++17", "-O2", "-pipe", "-static", "-s", str(source), "-o", str(output)],
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def build_submission(task: dict[str, Any], work_dir: Path, compile_time_limit: float = 20) -> Path:
    language = task["language"].lower()
    if language not in {"cpp", "c++", "cc"}:
        raise ValueError(f"Unsupported language: {task['language']}")

    source = work_dir / "main.cpp"
    executable = work_dir / "main"
    source.write_text(task["source_code"], encoding="utf-8")
    compile_cpp(source, executable, timeout=compile_time_limit)
    executable.chmod(0o755)
    return executable
