#include "testlib.h"

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    int a = inf.readInt(-1e3, 1e3, "a");
    inf.readSpace();
    int b = inf.readInt(-1e3, 1e3, "b");
    inf.readEof();
}