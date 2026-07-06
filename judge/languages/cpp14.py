class Executor:
    language_id = "cpp14"
    version = "g++ --version"
    command = "g++ -std=c++14 -Wall -DONLINE_JUDGE -O2 -lm -fmax-errors=5 -march=native -s {original_file} -o {output_file}"
    executable = ""
    # -Wl,-z,stack-size=66060288