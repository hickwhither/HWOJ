class Executor:
    language_id = "python"
    version = "python3 --version"
    command = "python3 -m -compileall -b {original_file} -o {output_file}"
    executable = "python3"
    example="print('Hello, world!')"