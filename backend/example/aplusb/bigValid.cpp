#include "testlib.h"

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    int a = inf.readInt(-1e9, 1e9, "a");
    inf.readSpace();
    int b = inf.readInt(-1e9, 1e9, "b");
    inf.readEof();
}