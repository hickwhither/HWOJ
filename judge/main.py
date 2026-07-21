from __future__ import annotations

import os
import argparse
import time
import importlib
import requests
from typing import Any
from urllib.parse import urljoin
import random, json
from dotenv import load_dotenv
load_dotenv()

parser = argparse.ArgumentParser(description="HWOJ judge worker")
parser.add_argument("--name", type=str, default="u")
parser.add_argument("--box_id", default=0)
parser.add_argument("--server_url", default="http://127.0.0.1:8000")
parser.add_argument("--poll_interval", type=float, default=3.0)
parser.add_argument("--once", action="store_true")
parser.add_argument("--work_dir", default=None, help="Directory for this worker temporary code/input/output/answer files")
args = parser.parse_args()

SECRET_KEY = os.getenv('SECRET_KEY')
JUDGER_NAME = args.name
BOX_ID = args.box_id
SERVER_URL = args.server_url
POLL_INTERVAL = args.poll_interval
WORK_DIR = args.work_dir or os.path.join("tmp", "judge", str(JUDGER_NAME))
os.makedirs(WORK_DIR, exist_ok=True)

languages = ["cpp", "python", "text"]
lang_dict = {}
for i in languages:
    module = importlib.import_module(f"languages.{i}")
    lang_dict[i] = module.Executor

def get_header():
    return {
        "Authorization": f"Bearer {SECRET_KEY}",
        "Content-Type": "application/json",
        "name": JUDGER_NAME,
        "message": random.choice([
            "bong thay minh qua dep trai",
            "uoc gi ta bot dang cap hon chut",
            "🐧",
            "vibe judger",
            "Wrong answer judger"
        ])
    }

def post(path: str, payload: dict = None) -> dict[str, Any]:
    payload = payload or {}
    headers = get_header()
    safe_headers = {
        k: (v.encode('utf-8').decode('latin-1').replace('\n', r'\\n') if isinstance(v, str) else v)
        for k, v in headers.items()
    }
    response = requests.post(urljoin(SERVER_URL, path), json=payload, headers=safe_headers, timeout=30)
    response.raise_for_status()
    return response.json() if response.text else None

from judgers import global_judge

if __name__ == "__main__":
    while True:
        try:
            task = post("/judger/get-task")
            if task:
                print(f"-> Đang chấm bài nộp ID: {task['id']} - {task['language']}")
                task['language'] = lang_dict[task['language']]
                result = global_judge(box_id=BOX_ID, work_dir=WORK_DIR, **task)
                result["id"] = task["id"]
                post("/judger/update-result", result)
                print(f"<- Đã gửi kết quả bài nộp ID: {task['id']} thành công.")
        except Exception as network_exc:
            print(f"[Lỗi kết nối hoặc Hệ thống]: {network_exc}")

        if args.once:
            break
            
        time.sleep(POLL_INTERVAL)