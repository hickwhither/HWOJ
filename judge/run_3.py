import subprocess
import threading
import sys
import os

"""
#include <iostream>\nusing namespace std;\nint a, b;\nint main(int argc, char* argv[]) {\n    cin >> a >> b;\n    cout << a+b;\n}
"""

JUDGER_SCRIPT = "main.py"
SERVER_URL = "http://127.0.0.1:8000"
POLL_INTERVAL = "3.0"

JUDGERS_CONFIG = [
    {"name": "Judger_Penguin_1", "box_id": "1"},
    {"name": "Judger_Penguin_2", "box_id": "2"},
    {"name": "Judger_Penguin_3", "box_id": "3"},
]

def log_reader(pipe, prefix):
    try:
        with pipe:
            for line in iter(pipe.readline, ""):
                print(f"[{prefix}] {line.strip()}", flush=True)
    except Exception as e:
        print(f"[{prefix} Error]: {e}", flush=True)

def start_judger(config, root_dir):
    name = config["name"]
    box_id = config["box_id"]
    
    box_dir = os.path.join(root_dir, f"run_box_{box_id}")
    os.makedirs(box_dir, exist_ok=True)
    
    script_path = os.path.join(root_dir, JUDGER_SCRIPT)
    
    cmd = [
        sys.executable, script_path,
        "--name", name,
        "--box_id", box_id,
        "--server_url", SERVER_URL,
        "--poll_interval", POLL_INTERVAL
    ]
    
    env = os.environ.copy()
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = root_dir + os.pathsep + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = root_dir

    print(f"[Hệ thống] Đang kích hoạt {name} trong thư mục: {box_dir}...")
    
    process = subprocess.Popen(
        cmd,
        cwd=box_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    t_out = threading.Thread(target=log_reader, args=(process.stdout, f"{name}-BOX{box_id}"))
    t_err = threading.Thread(target=log_reader, args=(process.stderr, f"{name}-BOX{box_id}-ERR"))
    
    t_out.daemon = True
    t_err.daemon = True
    t_out.start()
    t_err.start()
    
    return process

if __name__ == "__main__":
    print("=== TRÌNH QUẢN LÝ ĐA MÁY CHẤM PHÂN LẬP ===")
    
    root_directory = os.path.dirname(os.path.abspath(__file__))
    processes = []
    
    for config in JUDGERS_CONFIG:
        p = start_judger(config, root_directory)
        processes.append(p)
        
    print("[Hệ thống] Cả 3 máy chấm đã hoạt động độc lập. Nhấn Ctrl+C để dừng.\n")
    
    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\n[Hệ thống] Đang tắt toàn bộ máy chấm...")
        for p in processes:
            p.terminate()
        print("[Hệ thống] Đã tắt sạch sẽ.")