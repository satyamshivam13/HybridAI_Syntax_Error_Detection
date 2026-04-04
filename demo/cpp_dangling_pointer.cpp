#include <iostream>
using namespace std;

int* getValue() {
    int x = 42;
    return &x;
}

int main() {
    int* ptr = getValue();
    cout << *ptr << endl;
    return 0;
}
