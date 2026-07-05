from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

VERDICT_AC = "AC"


@dataclass(frozen=True)
class IsolateConfig:
    box_id: int = 0
    use_cgroups: bool = True
    wall_time_extra: float = 1.0


class IsolateRunner:
    """Run compiled submissions inside an isolate sandbox.

    The judge process is expected to run inside a Docker container that has
    isolate installed and enough privileges/cgroup mounts for isolate to work.
    """

    def __init__(self, config: IsolateConfig):
        self.config = config
        self.box_dir: Path | None = None

    def __enter__(self) -> "IsolateRunner":
        cmd = self._base_cmd() + ["--init"]
        self.box_dir = Path(subprocess.check_output(cmd, text=True).strip())
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        subprocess.run(self._base_cmd() + ["--cleanup"], check=False, capture_output=True, text=True)

    def run(self, executable: Path, input_path: Path, time_limit_ms: int, memory_limit_mb: int) -> dict:
        if self.box_dir is None:
            raise RuntimeError("isolate box has not been initialized")

        shutil.copy2(executable, self.box_dir / "solution")
        shutil.copy2(input_path, self.box_dir / "input.in")
        (self.box_dir / "solution").chmod(0o755)

        meta_file = self.box_dir.parent / "meta.txt"
        if meta_file.exists():
            meta_file.unlink()

        time_limit = max(time_limit_ms / 1000, 0.001)
        cmd = self._base_cmd() + [
            f"--meta={meta_file}",
            f"--time={time_limit}",
            f"--wall-time={time_limit + self.config.wall_time_extra}",
            f"--mem={memory_limit_mb * 1024}",
            "--stdin=input.in",
            "--stdout=output.out",
            "--stderr=error.err",
            "--run",
            "--",
            "./solution",
        ]
        process = subprocess.run(cmd, capture_output=True, text=True)
        meta = self._read_meta(meta_file)
        output = (self.box_dir / "output.out").read_bytes() if (self.box_dir / "output.out").exists() else b""
        stderr = (self.box_dir / "error.err").read_text(errors="replace") if (self.box_dir / "error.err").exists() else process.stderr

        return {
            "verdict": self._verdict(meta, process.returncode),
            "output": output,
            "stderr": stderr,
            "time": float(meta.get("time", 0) or 0),
            "memory": self._memory_mb(meta),
            "meta": meta,
        }

    def _base_cmd(self) -> list[str]:
        cmd = ["isolate", f"--box-id={self.config.box_id}"]
        if self.config.use_cgroups:
            cmd.insert(1, "--cg")
        return cmd

    @staticmethod
    def _read_meta(meta_file: Path) -> dict[str, str]:
        meta: dict[str, str] = {}
        if not meta_file.exists():
            return meta
        for line in meta_file.read_text(errors="replace").splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key] = value
        return meta

    @staticmethod
    def _memory_mb(meta: dict[str, str]) -> float:
        value = meta.get("cg-mem") or meta.get("max-rss") or "0"
        try:
            return float(value) / 1024
        except ValueError:
            return 0.0

    @staticmethod
    def _verdict(meta: dict[str, str], returncode: int) -> str:
        status = meta.get("status", "")
        if status == "TO":
            return "TLE"
        if status in {"XX", "FO"}:
            return "JE"
        if status in {"SG", "RE"}:
            return "MLE" if meta.get("exitsig") == "9" else "RE"
        if returncode != 0 or meta.get("exitcode", "0") != "0":
            return "RE"
        return VERDICT_AC
