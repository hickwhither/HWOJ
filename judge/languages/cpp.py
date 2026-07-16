class Executor:
    language_id = "cpp"
    file_extension = "cpp"
    compiled_file_extension = "out"
    version = "g++ --version"
    command = "g++ -std=c++14 -Wall -DONLINE_JUDGE -O2 -lm -fmax-errors=5 -march=native -s {original_file} -o {output_file}"
    executable = ""
    example="""#include<iostream>
    int main(){
        std::cout << "Hello, world!";
        return 0;
    }"""
    # -Wl,-z,stack-size=66060288