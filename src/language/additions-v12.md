# ZenCode 1.2 Extensions

## Tuples and destructuring

Tuples are immutable mini-structs and can be used as follows:

```
val a: (str, str) = ("a", "b"); // same as val a = ("a", "b")
val (x, y) = a; // tuple destructuring
```

Named tuples can be used also:

```
val a: (x: double, y: double) = (1, 1); // if not explicitly defined, would be inferred as (int, int)
doSomethingWith(a.x);
val {x, y} = a; // named destructuring
```

Objects can be destructured too:

```
class Foo {
    public val a: string;
    var _b: string;
    
    this(a: string, b: string) {
        this.a = a;
        this.b = b;
    }
    
    public get b => _b;
}

val foo = new Foo("a", "b");
val {a, b} = foo; // object destructuring
```
