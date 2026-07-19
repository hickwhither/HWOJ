import os, subprocess, shutil

last_update = {}
os.makedirs("cache", exist_ok=True)

from . import standard
def build_programs(problem_code: str, programs: dict[str, str]):
    target_dir = os.path.join("cache", problem_code)
    os.makedirs(target_dir, exist_ok=True)

    # Delete unused
    expected_files = set()
    for run_file in programs.keys():
        expected_files.add(run_file)
        expected_files.add(run_file + ".cpp")

    for filename in os.listdir(target_dir):
        if filename not in expected_files:
            file_path = os.path.join(target_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    # Process
    for run_file, source in programs.items():
        full_run_path = os.path.join(target_dir, run_file)
        full_cpp_path = full_run_path + ".cpp"
        
        need_compile = True
        print(full_cpp_path, os.path.exists(full_cpp_path))
        print(full_run_path, os.path.exists(full_run_path))
        if os.path.exists(full_cpp_path) and os.path.exists(full_run_path):
            print("!")
            with open(full_cpp_path, "r") as f:
                old_source = f.read()
            if old_source == source:
                print("!!")
                need_compile = False
        
        # Skip exists
        if not need_compile:
            print(f"Skip {full_run_path}")
            continue

        with open(full_cpp_path, "w") as f:
            f.write(source)
        compile_cmd = ["g++", "-O3", "-std=c++17", full_cpp_path, "-I.", "-o", full_run_path]
        
        try:
            print(f"Compiling {full_run_path}")
            res = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=30)
            # Delete if error
            if res.returncode != 0:
                if os.path.exists(full_cpp_path):
                    os.remove(full_cpp_path)
                if os.path.exists(full_run_path):
                    os.remove(full_run_path)
                return res.returncode, res.stderr
                
        except subprocess.TimeoutExpired: # Timeout
            # Delete if error
            if os.path.exists(full_cpp_path):
                os.remove(full_cpp_path)
            if os.path.exists(full_run_path):
                os.remove(full_run_path)
            return -1, "Compilation timed out"

    return 0, None

def build_submission(language:str, source:str):
    original_file = f"code.{language.file_extension}"
    output_file = f"code.{language.compiled_file_extension}"
    with open(f"code.{language.file_extension}", "w") as f: 
        f.write(source)
    res = subprocess.run(
        language.command.format(original_file=original_file, output_file=output_file).split(' '),
        capture_output=True,
        text=True,
        timeout=30
    )
    return res.returncode, res.stderr

def global_judge(box_id, language, source, problem, *args, **kwargs):
    try:
        returncode, error = build_programs(problem["code"], problem["programs"])
        if returncode:
            return {
                "status": "IE",
                "error": str(error)
            }
        returncode, error = build_submission(language, source)
        if returncode:
            return {
                "status": "CE",
                "error": str(error)
            }

        res = standard.judge(language.executable, f"./code.{language.compiled_file_extension}", problem, box_id)
        res['error'] = str(error)
        return res
    except Exception as exc:
        return {
            "status": "IE",
            "error": str(exc),
        }