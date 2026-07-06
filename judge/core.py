import subprocess
import os

def build_submission(language, source_code):
    with open("original", "w", encoding="utf-8") as f: f.write(source_code)
    res = subprocess.run(
        language.command.format(original_file="original", output_file="output").split(' '),
        check=True,
        capture_output=True,
        text=True,
        timeout=36
    )
    return res.returncode, res.stderr


def judge_task(isolate, submission_id, problem_code, config, language, source_code):
    code, err = build_submission(language, source_code)
    if code:
        return {
            "submission_id": submission_id,
            "status": "CE",
            "error": str(err),
        }
    os.system(f"sudo cp output {isolate.box_dir}")

    problem_dir = os.path.join("/app/problems", problem_code)
    test_cases = []
    for batch in config["batches"]:
        for test in batch["tests"]:
            if isinstance(test, (list, str)): # file
                input, output = test
                input_file = os.path.join(problem_dir, input)
                output_file = os.path.join(problem_dir, output)
            else: # gen
                input_file = "/app/input_file"
                output_file = "/app/output_file"
                subprocess.run(
                    [problem_dir] + test.split(' '),
                    stdout=open("/app/input_file","w"),
                    check=True
                )
                subprocess.run(
                    [problem_dir, config["answer"]],
                    stdout=open("/app/output_file","w"),
                    check=True
                )
            res = isolate.run(language.executable, input_file, output_file)
            res['batch'] = batch
            test_cases.append(res)
    return test_cases, err
