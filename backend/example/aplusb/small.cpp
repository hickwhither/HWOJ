#include "testlib.h"
#include <iostream>

using namespace std;

int main(int argc, char* argv[])
{
    registerGen(argc, argv, 1);
    cout << rnd.next((int)-1e3, (int)1e3) << ' ';
    cout << rnd.next((int)-1e3, (int)1e3);
}