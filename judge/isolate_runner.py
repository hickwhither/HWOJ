from __future__ import annotations

import os
import shutil
import subprocess

class IsolateRunner:
    def __init__(self, box_id=0, use_cgroups=True):
        self.box_id = box_id
        self.use_cgroups = use_cgroups
        self.box_dir: str | None = None

    def __enter__(self) -> "IsolateRunner":
        cmd = self._base_cmd() + ["--init"]
        self.box_dir = subprocess.check_output(cmd, text=True).strip()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        subprocess.run(self._base_cmd() + ["--cleanup"], check=False, capture_output=True, text=True)

    def run(self, executable: str, input_path: str, output_path: str, time_limit_ms: int, memory_limit_kb: int) -> dict:
        if self.box_dir is None:
            raise RuntimeError("isolate box has not been initialized")
        
        # path
        output_bin = os.path.join(self.box_dir, "output")
        box_input = os.path.join(self.box_dir, "input.in")
        
        shutil.copy2(executable, output_bin)
        shutil.copy2(input_path, box_input)
        os.chmod(output_bin, 0o755)

        meta_file = os.path.join(os.path.dirname(self.box_dir), "meta.txt")
        if os.path.exists(meta_file):
            os.remove(meta_file)

        time_limit = max(time_limit_ms / 1000, 0.001)
        cmd = self._base_cmd() + [
            f"--meta={meta_file}",
            f"--time={time_limit}",
            f"--wall-time={time_limit + 1}",
            f"--mem={memory_limit_kb}",
            "--stdin=input.in",
            "--stdout=output.out",
            "--stderr=error.err",
            "--run",
            "--",
            "./output",
        ]
        process = subprocess.run(cmd, capture_output=True, text=True)
        meta = self._read_meta(meta_file)
        
        # input
        actual_input_str = ""
        with open(output_path, "r", encoding="utf-8", errors="replace") as f:
            actual_input_str = f.read()

        # output
        box_output_file = os.path.join(self.box_dir, "output.out")
        actual_output_str = ""
        if os.path.exists(box_output_file):
            with open(box_output_file, "r", encoding="utf-8", errors="replace") as f:
                actual_output_str = f.read()
            
        # error
        box_error_file = os.path.join(self.box_dir, "error.err")
        if os.path.exists(box_error_file):
            with open(box_error_file, "r", encoding="utf-8", errors="replace") as f:
                error_data = f.read()
        else:
            error_data = process.stderr

        status = self._verdict(meta, process.returncode)
        # Chỉ check đáp án khi code không bị lỗi TLE, MLE, RE...
        if status is None:
            expected_output_str = ""
            if os.path.exists(output_path):
                with open(output_path, "r", encoding="utf-8", errors="replace") as f:
                    expected_output_str = f.read()
            
            # Tách chuỗi thành danh sách các token để so sánh
            actual_tokens = actual_output_str.split()
            expected_tokens = expected_output_str.split()
            
            if actual_tokens == expected_tokens:
                status = "AC"
            else:
                status = "WA"

        return {
            "status": status,
            "time_used": float(meta.get("time", 0) or 0),
            "memory_used": self._memory_mb(meta),
            "input_data":actual_input_str[:1024],
            "expected_output":expected_output_str[:1024],
            "actual_output": actual_output_str[:1024], 
            "error": error_data,
        }

    def _base_cmd(self) -> list[str]:
        cmd = ["sudo", "isolate", f"--box-id={self.box_id}"]
        if self.use_cgroups:
            cmd.insert(1, "--cg")
        return cmd

    @staticmethod
    def _read_meta(meta_file: str) -> dict[str, str]:
        meta: dict[str, str] = {}
        if not os.path.exists(meta_file):
            return meta
        with open(meta_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f.read().splitlines():
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
    def _verdict(meta: dict[str, str], returncode: int) -> str | None:
        status = meta.get("status", "")
        if status == "TO":
            return "TLE"
        if status in {"XX", "FO"}:
            return "JE"
        if status in {"SG", "RE"}:
            return "MLE" if meta.get("exitsig") == "9" else "RTE"
        if returncode != 0 or meta.get("exitcode", "0") != "0":
            return "RTE"
        return None