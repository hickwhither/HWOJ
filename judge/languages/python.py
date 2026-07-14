class Executor:
    language_id = "python"
    file_extension = "py"
    compiled_file_extension = "pyc"
    version = "python3 --version"
    command = "python3 -m -compileall -b {original_file}"
    executable = "python3"
    example="print('Hello, world!')"