import os, shutil, subprocess
from isolate_runner import isolate_run
from checkers import token
import mimetypes

def judge(executable, exec_path, problem_path, config, box_id=0):
    time_used = 0
    memory_used = 0
    test_cases = []
    total_score = 0
    max_score = 0

    for batch in config["batches"]:
        batch_score = batch.get("score", 0)
        max_score += batch_score
        batch_passed = True

        def run_test():
            nonlocal batch_passed, time_used, memory_used
            
            res = isolate_run(
                executable, exec_path, "input", "output", "error",
                config.get("time_limit", 2000),
                config.get("memory_limit", 32768),
                box_id
            )
            
            res['batch'] = batch
            
            if res['status']:
                res['verdict'] = res['status']
                res['status'] = None
                batch_passed = False 
            else:
                feedback = token.check() 
                res['verdict'] = 'WA' if feedback else 'AC'
                res['feedback'] = feedback
                if res['verdict'] == 'WA':
                    batch_passed = False
            
            time_used = max(time_used, res.get('time_used', 0))
            memory_used = max(memory_used, res.get('memory_used', 0))

            res['input'] = open("input", "r").read(128)
            res['output'] = open("output", "r").read(128)
            res['answer'] = open("answer", "r").read(128)
            res['error'] = open("error", "r").read(128)
            
            test_cases.append(res)

        for test in batch.get("tests", []):
            if not batch_passed: 
                break
            input_file, answer_file = test
            shutil.copy2(os.path.join(problem_path, input_file), "input")
            shutil.copy2(os.path.join(problem_path, answer_file), "answer")
            run_test()

        for gens in batch.get("generators", []):
            if not batch_passed:
                break
            subprocess.run(
                [problem_path + '/' + gens[0]] + gens[1:],
                stdout=open("input", "w"),
                check=True
            )
            subprocess.run(
                problem_path + '/' + config["answer"],
                stdin=open("input", "r"),
                stdout=open("answer", "w"),
                check=True
            )
            run_test()

        if batch_passed:
            total_score += batch_score

    percentage = total_score / max_score if max_score > 0 else 0.0

    return {
        'status': 'D',
        'time_used': time_used,
        'memory_used': memory_used,
        'percentage': percentage,
        'test_cases': test_cases
    }