
// fib from 0 - 65535, starting at (0, 1)
main = [] {
    int x = 0, y = 1, z = 0;

    while (x < 65535) {
        print(x);
        z = x + y;
        x = y;
        y = z;
    }
}