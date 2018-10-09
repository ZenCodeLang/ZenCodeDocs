# Deterministic Destruction

In the age of garbage collection, destruction has gone mostly ignored. For many cases, it isn't important either: objects are cleaned up by the garbage collector.

However, not everything can be managed by a garbage collector. File handles, for instance, need to be closed when they are no longer needed - not when the garbage collector decides to kick in. This has been mostly "solved" by closeables (or disposables, depending on the language you're used to). Yes these closeables have their own disadvantage: they need to be closed. And this isn't always trivial.

Surely, for cases where a resource (such as an open file) is used only within the context of a specific block statement, closing the resource is trivial - put it in a try-with-resources or using statement (or whatever else your language of choice may be using) and the resource will be closed whenever you're done. However, if such objects are passed to other methods or stored into a field, the case is far less trivial. That's where proper language support really benefits.

## Destructable types

In ZenCode, a destructable type is any kind of type that defines a destructor, as such:

```
class MyClass {
	this() {
		/* initialize some resource */
	}
	
	~this {
		/* cleanup some resource */
	}
}
```

Note that classes, structs and interfaces can all be destructible.

Values are destructed when they go out of scope. For instance, consider the following code:

```
class MyClass {
	val name as string;
	
	this(name as string) {
		this.name = name;
		println("Constructing " + name);
	}
	
	~this {
		println("Destructing " + name);
	}
}

val a = new MyClass("a");
val b = new MyClass("b");
```

Since both a and b go out of scope at the end of the script, this will print:

```
Constructing a
Constructing b
Destructing b
Destructing a
```

A value that is never stored will go out of scope immediately, thus if we changed the last lines to:

```
new MyClass("a");
new MyClass("b");
```

we would see a different output:

```
Constructing a
Destructing a
Constructing b
Destructing b
```

## Fields with destructable values

Object fields can be of a destructible type. If a class contains any fields of destructible types, the class itself will automatically become destructible too. This may eventually cascade further to parent types. Additionally, type expansions cannot define destructible fields. When a class with destructible fields is destructed, the destructible fields will automatically be cleaned up as well.

~~~ MORE ~~~

## Casting

A destructible value can only be cast to a target type is also destructible, unless a guarantee can be given that the value is not destructed while in use. Additionally, if a type is destructible, its supertype must also be destructible, and vice versa. This ensures that destruction is always guaranteed, even if a value has been casted to a supertype or interface value.

For instance, consider the following code:

```
interface MyInterface1 {
	~this;
}

interface MyInterface2 {
}

class MyClass {
	~this;
	
	public implements MyInterface1 {}
	public implements MyInterface2 {}
}

function testA1(value as MyInterface1`unique) {
	/* ... */
	/* value will be destructed here, `unique guarantees that this is the only instance */
}

function testA2(value as MyInterface1`borrow) {
	/* ... */
}

function testB1(value as MyInterface2`unique) {
	/* ... */
	/* (value is not destructible) */
}

function testB2(value as MyInterface2`borrow) {
	/* ... */
}

testA1(new MyClass()); // OK, MyInterface1 is destructible
testA2(new MyClass()); // OK, MyInterface1 is destructible
testB1(new MyClass()); // compile-time error: cannot cast destructible to nondestructible type
testB2(new MyClass()); // OK, borrowing the value, will be destructed *after* the method returns
```

Note that we could also replace `unique with `shared here (or omit entirely and let it default to `shared) and it would work precisely the same for this example.
