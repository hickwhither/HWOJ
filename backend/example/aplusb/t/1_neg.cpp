#include <bits/stdc++.h>
using namespace std;

#define int long long

mt19937_64 rng;

int Rand(int l,int r){
    return uniform_int_distribution<int>(l,r)(rng);
}

signed main(int argc,char *argv[]){
    rng.seed(atoi(argv[1]));

    cout << Rand(-1e4,1) << " " << Rand(-1e4,1) << endl;
}