import os
import shutil, json
import subprocess
from isolate_runner import isolate_run
from checkers import token

def judge(executable, exec_path, problem, box_id=0):
    time_used = 0
    memory_used = 0
    test_cases_results = []
    total_score = 0
    max_score = 0

    answer = os.path.join("cache", problem["code"], "answer")
    for subname, subtask in problem["subtasks"].items():
        group_passed = True
        max_score += subtask["points"]
        generator = os.path.join("cache", problem["code"], subtask["generator"])
        validator = os.path.join("cache", problem["code"], subtask["validator"])
        for s in subtask["seeds"]:
            # Run
            subprocess.run([generator, str(s)], stdout=open("input", "w"))
            subprocess.run([answer], stdin=open("input", "r"), stdout=open("answer", "w"))
            res = isolate_run(
                executable, exec_path, "input", "output", "error",
                problem.get("time_limit", 2000),
                problem.get("memory_limit", 32768),
                box_id
            )
            res["subtask"] = subname

            # Verdict
            feedback = token.check()
            res['verdict'] = 'WA' if feedback else 'AC'
            res['feedback'] = feedback
            if res['verdict'] == 'WA':
                group_passed = False
                break
            
            # Time memory
            time_used = max(time_used, res.get('time_used', 0))
            memory_used = max(memory_used, res.get('memory_used', 0))

            # File read
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
        
        if group_passed:
            total_score += subtask["points"]

    percentage = total_score / max_score if max_score > 0 else 0.0

    return {
        'status': 'D',
        'time_used': time_used,
        'memory_used': memory_used,
        'percentage': percentage,
        'test_cases': test_cases_results
    }
