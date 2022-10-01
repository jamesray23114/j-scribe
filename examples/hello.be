int a;               // pass
ptr b;               // pass
int<int> c;          // type 'int' cannot have modifiers
func<int> d;         // pass
func<int -> int> e;  // pass
ptr<x> f;            // invalid type 'x'
ptr<int> g;          // pass
ptr<ptr<int>> h;     // pass
ptr<int -> int> i;   // pointer type cannot have return types
x j;                 // invalid type 'x'