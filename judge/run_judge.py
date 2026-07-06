from __future__ import annotations

import argparse
import time
import importlib
import requests
from typing import Any
from urllib.parse import urljoin
from datetime import datetime
import random

from core import judge_task
from isolate_runner import IsolateRunner

parser = argparse.ArgumentParser(description="EPenguinOJ judge worker")
parser.add_argument("--name", type=str, default=None)
parser.add_argument("--key", type=str)
parser.add_argument("--server_url", default="http://127.0.0.1:8000")
parser.add_argument("--poll_interval", type=float, default=3.0)
parser.add_argument("--once", action="store_true")
args = parser.parse_args()

JUDGER_NAME = args.name
JUDGER_KEY = args.key
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
        "uoc gi minh bot dang cap",
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

while True:
    try:
        task = post("/judger/get-task")
        
        if task:
            sub_id = task["id"] 
            print(f"-> Đang chấm bài nộp ID: {sub_id} ({task['language']})")
            
            try:
                isolate = IsolateRunner()
                test_cases, err = judge_task(
                    isolate=isolate,
                    submission_id=sub_id,
                    problem_code=task["problem_code"],
                    config=task.get("config"), # .get đề phòng trường hợp không có config bài
                    language=lang_dict[task["language"]],
                    source_code=task["source_code"],
                )
                
                # SỬA LỖI LOGIC: Tính toán lại tổng time và memory từ mảng test_cases đúng cách
                total_time = 0.0
                total_memory = 0.0
                if isinstance(test_cases, list):
                    for tc in test_cases:
                        total_time += tc.get("time_used", 0)
                        total_memory += tc.get("memory_used", 0)
                
                result = {
                    "submission_id": sub_id,
                    "status": "D", # Hoặc trạng thái hoàn thành của hệ thống bạn (ví dụ: "AC", "WA"...)
                    "time_used": total_time,
                    "memory_used": total_memory,
                    "error": str(err) if err else None,
                    "test_cases": test_cases
                }
            except Exception as exc:
                result = {
                    "submission_id": sub_id,
                    "status": "IE", # Internal Error
                    "error": str(exc),
                }
                
            # Gửi kết quả về backend thông qua Header Authentication
            post("/judger/update-result", result)
            print(f"<- Đã gửi kết quả bài nộp ID: {sub_id} thành công.")
            
    except Exception as network_exc:
        print(f"[Lỗi kết nối hoặc Hệ thống]: {network_exc}")

    if args.once:
        break
        
    time.sleep(POLL_INTERVAL)