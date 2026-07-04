import subprocess
import os

def run_submission(executable_path, input_file_path, box_id=0, time_limit=2.0, memory_limit=512):
    """
    Chạy code thí sinh trong isolate sandbox.
    
    :param executable_path: Đường dẫn tới file C++ đã biên dịch của thí sinh.
    :param input_file_path: Đường dẫn tới file testX.in
    :param box_id: ID của sandbox (dùng khi chạy song song nhiều worker).
    :param time_limit: Giới hạn thời gian (giây).
    :param memory_limit: Giới hạn RAM (MB).
    """
    
    # Bước 1: Khởi tạo box
    # --cg: Kích hoạt Control Groups (bắt buộc trên các hệ thống Linux mới để đo RAM/Time)
    init_cmd = f"isolate --cg -b {box_id} --init"
    box_path = subprocess.check_output(init_cmd, shell=True, text=True).strip()
    
    # box_path thường nằm ở dạng: /var/local/lib/isolate/0/box
    
    # Bước 2: Chuẩn bị file vào box
    os.system(f"cp {executable_path} {box_path}/solution")
    os.system(f"cp {input_file_path} {box_path}/input.in")
    
    meta_file = f"/tmp/meta_{box_id}.txt"
    
    # Bước 3: Thiết lập lệnh chạy isolate
    run_cmd = [
        "isolate",
        "--cg",                  # Bật Control Groups
        f"-b={box_id}",          # Chỉ định box ID
        f"-M={meta_file}",       # File lưu kết quả đo đếm tài nguyên (Meta)
        f"-t={time_limit}",      # Giới hạn thời gian CPU (CPU time)
        f"-w={time_limit + 1}",  # Giới hạn thời gian thực tế (Wall time) - thường cho nhỉnh hơn chút
        f"-m={memory_limit * 1024}", # Giới hạn RAM (isolate tính bằng KB)
        "-i=input.in",           # Redirect stdin từ file input.in
        "-o=output.out",         # Redirect stdout ra file output.out
        "-e=error.err",          # Redirect stderr
        "--run",                 # Lệnh báo hiệu bắt đầu chạy
        "--",                    # Ngăn cách cờ của isolate và lệnh cần chạy
        "./solution"             # Lệnh thực thi bên trong box
    ]
    
    # Thực thi mã
    process = subprocess.run(run_cmd, capture_output=True, text=True)
    
    # Bước 4: Đọc file Meta để biết trạng thái
    status = "OK"
    time_used = 0.0
    memory_used = 0
    exit_code = 0
    
    if os.path.exists(meta_file):
        with open(meta_file, 'r') as f:
            for line in f:
                key, val = line.strip().split(':', 1)
                if key == 'time':
                    time_used = float(val)
                elif key == 'cg-mem': # Nếu dùng --cg thì đọc cg-mem
                    memory_used = float(val) / 1024 # Đổi về MB
                elif key == 'exitcode':
                    exit_code = int(val)
                elif key == 'status':
                    status = val # Có thể là TO (Time Out), SG (Signal - thường là MLE hoặc RE)
                    
        os.remove(meta_file)

    # Lấy output của thí sinh
    output_content = ""
    output_file = f"{box_path}/output.out"
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            output_content = f.read()

    # Bước 5: Dọn dẹp sandbox
    cleanup_cmd = f"isolate --cg -b {box_id} --cleanup"
    subprocess.run(cleanup_cmd, shell=True)

    # Phân tích kết quả
    verdict = "AC/WA (Cần Check)"
    if status == "TO":
        verdict = "TLE"
    elif status == "SG":
        if "Killed" in process.stderr or exit_code == 9: 
            # Bị hệ điều hành kill thường do out of memory
            verdict = "MLE"
        else:
            verdict = "RE"
    elif exit_code != 0:
        verdict = "RE"

    return {
        "verdict": verdict,
        "time_used": time_used,
        "memory_used": memory_used,
        "output": output_content
    }