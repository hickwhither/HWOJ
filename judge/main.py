from __future__ import annotations

import argparse
import time
import importlib
import requests
from typing import Any
from urllib.parse import urljoin
import random, json
import os, subprocess
from dotenv import load_dotenv
load_dotenv()

PROBLEM_PATH = "/app/problems"
JUDGER_KEY = os.getenv('JUDGER_KEY')

try:
    from .local_settings import *
except ImportError:
    pass

parser = argparse.ArgumentParser(description="HWOJ judge worker")
parser.add_argument("--name", type=str, default=None)
parser.add_argument("--box_id", default=0)
parser.add_argument("--server_url", default="http://127.0.0.1:8000")
parser.add_argument("--poll_interval", type=float, default=3.0)
parser.add_argument("--once", action="store_true")
args = parser.parse_args()

JUDGER_NAME = args.name
BOX_ID = args.box_id
SERVER_URL = args.server_url
POLL_INTERVAL = args.poll_interval

languages = ["cpp", "python"]
lang_dict = {}
for i in languages:
    module = importlib.import_module(f"languages.{i}")
    lang_dict[i] = module.Executor

def get_header():
    return {
        "name": JUDGER_NAME,
        'authentication': JUDGER_KEY,
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

from judge.judgers import dmoj

def compile_problem_sources(problem_path: str):
    for root, dirs, files in os.walk(problem_path):
        for file in files:
            if file.endswith(".cpp"):
                cpp_file_path = os.path.join(root, file)

                file_name_without_ext = os.path.splitext(file)[0]
                output_path = os.path.join(root, file_name_without_ext)

                should_compile = False
                if not os.path.exists(output_path):
                    should_compile = True
                else:
                    # Nếu file .cpp được chỉnh sửa sau khi file chạy được tạo -> cần compile lại
                    cpp_mtime = os.path.getmtime(cpp_file_path)
                    out_mtime = os.path.getmtime(output_path)
                    if cpp_mtime > out_mtime:
                        should_compile = True
                
                if should_compile:
                    compile_cmd = ["g++", "-O3", "-std=c++17", cpp_file_path, "-o", output_path]
                    try:
                        subprocess.run(compile_cmd, check=True, capture_output=True, text=True, timeout=30)
                        print(f"   [Biên dịch thành công]: {file} -> {file_name_without_ext}")
                    except subprocess.CalledProcessError as e:
                        print(f"   [Lỗi biên dịch {file}]: {e.stderr}")
                    except subprocess.TimeoutExpired:
                        print(f"   [Timeout] Biên dịch {file} quá 30 giây.")

def build_submission(language, source):
    original_file = f"code.{language.file_extension}"
    output_file = f"code.{language.compiled_file_extension}"
    with open(f"code.{language.file_extension}", "w", encoding="utf-8") as f: 
        f.write(source)
    res = subprocess.run(
        language.command.format(original_file=original_file, output_file=output_file).split(' '),
        check=True,
        capture_output=True,
        text=True,
        timeout=36
    )
    return res.returncode, res.stderr

def run(language, source, problem_code, box_id):
    try:
        # 1. Biên dịch code nộp của thí sinh
        returncode, error = build_submission(language, source)
        if returncode:
            return {
                "status": "CE",
                "error": str(error)
            }
            
        problem_path = os.path.join(PROBLEM_PATH, problem_code)
        compile_problem_sources(problem_path)
            
        config = json.load(open(os.path.join(problem_path, '.json'), 'r'))

        res = dmoj.judge(language.executable, f"./code.{language.compiled_file_extension}", problem_path, config, box_id)
        res['error'] = str(error)
        return res
    except Exception as exc:
        return {
            "status": "IE",
            "error": str(exc),
        }

if __name__ == "__main__":
    while True:
        try:
            task = post("/judger/get-task")
            if task:
                print(f"-> Đang chấm bài nộp ID: {task['id']} ({task['language']})")
                result = run(lang_dict[task['language']], task['source'], task['problem_code'], BOX_ID)
                result["id"] = task["id"]
                post("/judger/update-result", result)
                print(f"<- Đã gửi kết quả bài nộp ID: {task['id']} thành công.")
        except Exception as network_exc:
             print(f"[Lỗi kết nối hoặc Hệ thống]: {network_exc}")

        if args.once:
            break
            
        time.sleep(POLL_INTERVAL)