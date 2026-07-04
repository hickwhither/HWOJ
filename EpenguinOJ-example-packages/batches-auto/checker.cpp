#include "testlib.h"

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);

    int pans = ouf.readInt(-2000, 2000, "sum of numbers");
    int jans = ans.readInt();
    
    if (pans == jans)
        quitf(_ok, "The sum is correct.");
    else
        quitf(_wa, "The sum is wrong: expected = %d, found = %d", jans, pans);
}