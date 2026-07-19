#include "testlib.h"

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);

    int n = inf.readInt(1, 1e6);
    for(int i=1; i<=n; ++i){
        int c = inf.readInt(-1e9, 1e9);
        int a = ouf.readInt(-1e9, 1e9);
        int b = ouf.readInt(-1e9, 1e9);
        if(a+b!=c){
            quitf(_wa, "#i: The sum is wrong: %d+%d = %d, expected %d", a, b, a+b, c);
        }
    }
    
    quitf(_ok, "The sum is correct.");
}