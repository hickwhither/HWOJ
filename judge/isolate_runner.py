from __future__ import annotations
import os
import shutil
import subprocess
from contextlib import contextmanager

def _base_cmd(box_id: int, use_cgroups: bool) -> list[str]:
    cmd = ["sudo", "isolate", f"--box-id={box_id}"]
    if use_cgroups:
        cmd.insert(1, "--cg")
    return cmd

@contextmanager
def isolate_sandbox(box_id: int = 0, use_cgroups: bool = True):
    """Context manager khởi tạo và tự động dọn dẹp sandbox cho 1 test case."""
    cmd = _base_cmd(box_id, use_cgroups) + ["--init"]
    box_dir = subprocess.check_output(cmd, text=True).strip()
    try:
        yield box_dir
    finally:
        # Chạy xong test (dù thành công hay lỗi) đều xóa sạch box ngay lập tức
        subprocess.run(_base_cmd(box_id, use_cgroups) + ["--cleanup"], check=False, capture_output=True)

def isolate_run(
    executable: str,
    exec_path: str,
    input_path: str,
    output_path: str,
    error_path: str,
    time_limit: int, # secs
    memory_limit: int, # KB
    box_id: int = 0,
    use_cgroups: bool = True
) -> dict:
    with isolate_sandbox(box_id, use_cgroups) as box_dir:
        # 1. Define Files
        box_exec = os.path.join(box_dir, "a")
        box_in = os.path.join(box_dir, "input.in")
        box_out = os.path.join(box_dir, "output.out")
        box_err = os.path.join(box_dir, "error.err")
        # Copy file vào sandbox
        shutil.copy2(exec_path, box_exec)
        shutil.copy2(input_path, box_in)
        os.chmod(box_exec, 0o755)
        # Chuẩn bị file meta ở ngoài
        meta_file = os.path.join(os.path.dirname(box_dir), f"meta_{box_id}.txt")
        if os.path.exists(meta_file): os.remove(meta_file)

        # 2. Execute
        cmd = _base_cmd(box_id, use_cgroups) + [
            f"--meta={meta_file}",
            f"--time={time_limit}",
            f"--wall-time={time_limit + 2}",
            f"--mem={memory_limit}",
            "--stdin=input.in",
            "--stdout=output.out",
            "--stderr=error.err",
            "--run", "--", executable, "./a",
        ]
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        # 3. Read meta + copy files
        meta: dict[str, str] = {}
        if os.path.exists(meta_file):
            with open(meta_file, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if ":" in line:
                        k, v = line.strip().split(":", 1)
                        meta[k] = v
            os.remove(meta_file) # Đọc xong xóa luôn file meta bên ngoài

        # 4. output/error
        shutil.copy2(box_out, output_path)
        shutil.copy2(box_err, error_path)

        # 5. Status
        status = meta.get("status", "")
        if status == "TO": status = "TLE"
        elif status in {"XX", "FO"}: status = "IE"
        elif status in {"SG", "RE"}:
            status = "MLE" if meta.get("exitsig") == "9" else "RTE"
        elif process.returncode != 0 or meta.get("exitcode", "0") != "0":
            status = "RTE"

        mem_val = meta.get("cg-mem") or meta.get("max-rss") or "0"

        return {
            "status": status,
            "time_used": float(meta.get("time", 0) or 0),
            "memory_used": float(mem_val)
        }