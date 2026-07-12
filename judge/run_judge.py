from __future__ import annotations

import argparse
import time
import importlib
import requests
from typing import Any
from urllib.parse import urljoin
from datetime import datetime
import random, json
import os, subprocess

parser = argparse.ArgumentParser(description="EPenguinOJ judge worker")
parser.add_argument("--name", type=str, default=None)
parser.add_argument("--key", type=str)
parser.add_argument("--box_id", default=0)
parser.add_argument("--server_url", default="http://127.0.0.1:8000")
parser.add_argument("--poll_interval", type=float, default=3.0)
parser.add_argument("--once", action="store_true")
args = parser.parse_args()

JUDGER_NAME = args.name
JUDGER_KEY = args.key
BOX_ID = args.box_id
SERVER_URL = args.server_url
POLL_INTERVAL = args.poll_interval

def post(path: str, payload: dict = None) -> dict[str, Any]:
    payload = payload or {}
    headers = {"X-Judge-Key": JUDGER_KEY}
    response = requests.post(urljoin(SERVER_URL, path), json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json() if response.text else None

languages = ["cpp14", "python3"]
lang_dict = {}
for i in languages:
    module = importlib.import_module(f"languages.{i}")
    lang_dict[i] = module.Executor

post("/judger/ping", {
    "name": JUDGER_NAME,
    "languages": languages,
    "start_time": datetime.now(),
    "description": random.choices([
        "bong thay minh qua dep trai",
        "uoc gi ta bot dang cap hon chut",
        "uocj bi gs chit",
        "chit chet chit chet",
        "🐧",
        "cut cut cut cut cut cut cut cut cut cut cut cut cut cut cut",
        "⚠️⚠️⚠️ ⚠️⚠️ ⚠️⚠️⚠️⚠️⚠️ ⚠️⚠️⚠️⚠️⚠️⚠️ ⚠️⚠️⚠️",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "vibe judger",
        "Nay khong có gì ăn roiii",
        "Ăn tạm buồi a đi 😘",
        "Trí tuệ nhân tạo đang hot mà ko tuyển thêm chuyên tin?",
        "Đại học robl0x, CHÚC MỪNG TUYỂN THẲNG!!!",
        """UNDER CONSTRUCTION\nCome back soon~""",
        """DH DONG A Chuc mung VIET dat diem cao ky thi THPT!
        Em du dieu kien xet Hoc bong Tai nang cua Truong dac biet tai nganh Y KHOA, DUOC, LUAT.
        Hoan tat ho so tai oj.hw.io.vn de dang ky, tra cuu ket qua va duoc tu van hoc bong.
        LH 069696969 em nhe!
        """,
        "Trường đại học ZZZ",
        "Wrong answer judger",
    ])
})

print(f"Worker [{JUDGER_NAME}] đang chạy và đợi bài...")

from judgers import standard

def build_submission(language, source):
    with open("code", "w", encoding="utf-8") as f: f.write(source)
    res = subprocess.run(
        language.command.format(original_file="code", output_file="exec_code").split(' '),
        check=True,
        capture_output=True,
        text=True,
        timeout=36
    )
    return res.returncode, res.stderr

def run(language, source, problem_code):
    try:
        returncode, error = build_submission(language, source)
        if returncode:
            return {
                "status": "CE",
                "error": str(error)
            }
        problem_path = os.path.join("app", "problems", problem_code)
        config = json.loads(os.path.join(problem_path, '.json'))
        
        res = standard.judge(language, "exec_code", problem_path, config, BOX_ID)
        res['error'] = str(error)
        return res
    except Exception as exc:
        return {
            "status": "IE", # Internal Error
            "error": str(exc),
        }

while True:
    try:
        task = post("/judger/get-task")
        
        if task:
            print(f"-> Đang chấm bài nộp ID: {task['id']} ({task['language']})")
            result = run(lang_dict(task['language']), task['source'], task['problem_code'])
            result["id"] = task["id"]
            post("/judger/update-result", result)
            print(f"<- Đã gửi kết quả bài nộp ID: {task['id']} thành công.")
            
    except Exception as network_exc:
        print(f"[Lỗi kết nối hoặc Hệ thống]: {network_exc}")

    if args.once:
        break
        
    time.sleep(POLL_INTERVAL)