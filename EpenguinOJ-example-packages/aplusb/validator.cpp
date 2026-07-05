#include "testlib.h"

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    
    int testCount = inf.readInt(1, 10, "testCount");
    inf.readEoln();
    
    for (int i = 0; i < testCount; i++) {
        setTestCase(i + 1);
        int n = inf.readInt(1, 100, "n");
        inf.readSpace();
        inf.readInt(1, 1'000'000, "w");
        inf.readEoln();

        inf.readInts(n, 1, 1000, "p");
        inf.readEoln();
    }

    inf.readEof();
}