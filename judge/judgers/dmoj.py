import os
import shutil
import subprocess
import zipfile
import yaml
from isolate_runner import isolate_run
from checkers import token

def judge(executable, exec_path, problem_path, box_id=0):
    time_used = 0
    memory_used = 0
    test_cases_results = []
    total_score = 0
    max_score = 0

    # 1. Đọc file cấu hình (config.yml hoặc init.yml)
    config_file = os.path.join(problem_path, "init.yml")
    if not os.path.exists(config_file):
        config_file = os.path.join(problem_path, "config.yml")
        
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 2. Giải nén file archive (test.zip) ra thư mục cache
    archive_name = config.get("archive")
    cache_dir = os.path.join(problem_path, ".cache_unzip")
    
    if archive_name:
        archive_path = os.path.join(problem_path, archive_name)
        # Chỉ giải nén nếu thư mục cache chưa tồn tại (tối ưu tốc độ các lần chấm sau)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(cache_dir)
    else:
        cache_dir = problem_path # Fallback nếu không có file zip

    # 3. Phân tích loại Checker
    checker_config = config.get("checker", "standard")
    is_testlib = isinstance(checker_config, dict) and checker_config.get("name") == "bridged"
    
    # 4. Duyệt qua danh sách test cases
    for tc_group in config.get("test_cases", []):
        is_batched = "batched" in tc_group
        # Lấy danh sách bài test trong group hiện tại
        tests = tc_group["batched"] if is_batched else [tc_group]
        group_points = tc_group.get("points", 0)
        max_score += group_points

        group_passed = True # Cờ xác định subtask/batch này có đúng toàn bộ không

        for test in tests:
            if not group_passed and is_batched:
                break # Tối ưu: Nếu 1 test trong batch sai, bỏ qua luôn các test còn lại trong batch đó
            
            in_file = test["in"]
            out_file = test["out"]

            # Copy file input và file answer từ cache ra không gian chấm
            shutil.copy2(os.path.join(cache_dir, in_file), "input")
            shutil.copy2(os.path.join(cache_dir, out_file), "answer")

            # Xóa file output cũ nếu có để tránh ghi đè sai
            if os.path.exists("output"):
                os.remove("output")

            # Chạy Isolate Sandbox
            res = isolate_run(
                executable, exec_path, "input", "output", "error",
                config.get("time_limit", 2000),
                config.get("memory_limit", 32768),
                box_id
            )
            
            res['test_file'] = in_file
            res['is_batched'] = is_batched

            if res.get('status'):
                # Lỗi Time Limit (TLE), Memory Limit (MLE), Runtime Error (RTE), v.v.
                res['verdict'] = res['status']
                res['status'] = None
                group_passed = False 
            else:
                # Code chạy xong (Exit Code 0), tiến hành check output
                if is_testlib:
                    # Chạy custom testlib checker (Giả định file checker đã được biên dịch sẵn thành 'checker.out')
                    # Cú pháp chuẩn của testlib: <checker> <input> <output> <answer>
                    checker_bin = os.path.join(problem_path, "checker.out")
                    try:
                        chk_process = subprocess.run(
                            [checker_bin, "input", "output", "answer"],
                            capture_output=True, text=True
                        )
                        feedback = chk_process.stdout + chk_process.stderr
                        
                        # Testlib trả về exit_code 0 là AC, khác 0 là WA/PE
                        if chk_process.returncode != 0:
                            res['verdict'] = 'WA'
                            group_passed = False
                        else:
                            res['verdict'] = 'AC'
                        res['feedback'] = feedback[:128] # Lấy 128 ký tự log của testlib
                    except Exception as e:
                        res['verdict'] = 'JE' # Judge Error (Lỗi hệ thống chấm)
                        res['feedback'] = str(e)[:128]
                        group_passed = False
                else:
                    # Chạy checker standard (token-based diff)
                    feedback = token.check()
                    res['verdict'] = 'WA' if feedback else 'AC'
                    res['feedback'] = feedback
                    if res['verdict'] == 'WA':
                        group_passed = False

            # Cập nhật Max Time và Max Memory
            time_used = max(time_used, res.get('time_used', 0))
            memory_used = max(memory_used, res.get('memory_used', 0))

            # Hàm phụ đọc file an toàn (tránh văng lỗi nếu thí sinh không in ra file)
            def safe_read(filename):
                if os.path.exists(filename):
                    with open(filename, "r", errors='ignore') as f:
                        return f.read(128)
                return ""

            res['input'] = safe_read("input")
            res['output'] = safe_read("output")
            res['answer'] = safe_read("answer")
            res['error'] = safe_read("error")
            
            test_cases_results.append(res)

        # Cộng điểm nếu pass toàn bộ test trong subtask/batch (hoặc pass test lẻ)
        if group_passed:
            total_score += group_points

    percentage = total_score / max_score if max_score > 0 else 0.0

    return {
        'status': 'D', # Done
        'time_used': time_used,
        'memory_used': memory_used,
        'percentage': percentage,
        'test_cases': test_cases_results
    }