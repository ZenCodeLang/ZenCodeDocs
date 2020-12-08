# ZenCode 2.0 Extensions

## Destructable values

Classes can now also have a destructor, which is defined as follows:

```
class MyClass {
	this() {
		println("Constructor called");
	}
	
	~this {
		println("Destructor called");
	}
}
```

A class with destructor is called a destructible class and will have its destructor called as soon as all of its usages go out of scope. Even in a garbage collected environment, the destructor will be called immediately:

```
{
	var a = new MyClass(); // calls the constructor
	// the destructor will be called here (even if an exception occurs)
}
```

A class with a field of destructable type will also automatically be a destructible class, even if it doesn't have an explicit destructor defined. Thus the following class would be destructible as well:

```
class OtherClass {
	val item: MyClass;
	
	this() {
		item = new MyClass();
	}
}

{
	var a = new OtherClass();
	// the destructor of the MyClass item field in a will be called here
}
```

It is not allowed to cast a destructible class to a non-destructible interface. To support such conversion, a destructible interface must be defined by adding `~this;` as a member to turn the interface to a destructible interface:

```
interface MyInterfaceA {
}

interface MyInterfaceB {
	~this;
}

class MyClass {
	this() {
	}
	
	~this {
		println("Destructor called");
	}
	
	// this is allowed, as we will see later
	public implements MyInterfaceA;
	public implements MyInterfaceB;
}

{
	var a = new MyClass();
	var b: MyInterfaceA = a; // error: conversion of destructible class to non-destructible interface not allowed
	var c: MyInterfaceB = a; // OK
}
```

## Borrowing

It is possible to indicate temporary use of an object by borrowing it:

```
function myFunction(a: &MyClass) {
}

{
	var a = new MyClass();
	myFunction(a);
}
```

It is allowed to borrow from a destructible class to a non-destructible interface when borrowing the value:

```
function myFunction(a: &MyInterfaceA) {
}

{
	var a = new MyClass();
	myFunction(a); // OK now
}
```

Borrowed values must not escape, thus for instance, the following is not allowed:

```
class OtherClass {
	var a: MyClass;
	
	this() {
		a = new MyClass();
	}
	
	myFunction(value: &MyClass) {
		a = value; // error: attempting to store a borrowed value
	}
}
```

When handling destructible values and objects in a reference-counted system, borrowed values will improve performance because the runtime doesn't need to track usage of these values - it can be statically verified.

It is only possible to call methods on a borrowable object if the method is marked as such with the & prefix, which essentially borrows `this`:

```
class Foo {
	val name: string;
	
	this(name: string) {
		this.name = name;
	}
	
	&myFunction() {
		println("Name: " + this.name);
	}
}
```

It is thus good practice to mark methods with & whenever it is possible to do so. However, methods which borrow this cannot leak this, thus it cannot always be used.

## Explicit ownership: unique values

It is possible to mark function arguments and fields as unique, which means that no other references to the same object may exist, with the exception of borrowed values. In order to construct a unique value, a `unique` tagged constructor is needed as well.

Unique tagged values use move semantics - this is, the value can be passed as unique argument to a function, or moved to an unique field, but the original value cannot be used afterwards.

```
myFunction(a: unique string) {
	println("Hello " + a);
}

var a: unique string = "world";
myFunction(a); // OK, will move the object ownership to myFunction
println("Hello " + a); // error: attempting to use a moved object
```

It is also possible to move a unique value to a "normal" value:

```
class MyClass {
	public var a: unique string = "";
	public var b: string = "";
}

var a: unique string = "world";
var object = new MyClass();
object.a = a; // OK

var b: unique string = "other";
object.b = b; // also OK
```

The other way around is not permitted:

```
var a = "world";
var object = new MyClass();
object.a = a; // error: attempting to move non-unique to unique value
```

If a constructor should return a unique value, a unique constructor must be defined:

```
class MyClass {
	public val name: string;
	
	unique this(name: string) {
		this.name = name;
	}
}

val a: unique MyClass = new MyClass("x");
```

Unique constructors cannot leak `this` to other methods, unless `this` is borrowed:

```
class MyClass {
	public val name: string;
	
	unique this(name: string) {
		this.name = string;
		doFoo(); // error: cannot pass unique value to shared method
		doBar(); // OK
	}
	
	doFoo() {
		// never know if this method leaks this...
	}
	
	&doBar() {
		// OK, this guaranteed not to leak
	}
}
```

Unique values don't need refcounting and thus may improve performance on reference counted systems or on destructable values.

## Unique methods

A class or interface may also contain a unique method, which can only be used on a unique value, and which will consume the value:

```
class MyClass {
	unique consume() {
		...
	}
}

val a = new MyClass();
a.consume();
// variable a has been moved and can no longer be used here
```

This function can come in handy in builder methods, such as the one illustrated below.

## take and swap

Two new built-in methods are available, which are particularly useful on unique values: `swap` will, as expected, swap out two values; whereas `take` will replace a value with its default or a given value (when using the 2-argument variant). Using the 1-argument variant of `take` on a variable or field which has no default value is an error.

```
class MyBuilder {
	public var x: unique string;
	public var y: unique string?;
	
	swapXY() {
		swap(x, y);
	}
	
	unique build() {
		var x = "";
		swap(x, this.y);
		return new MyClass(x, take(y)); // can use take on y, which will replace it with null
		// equivalent code:
		// return new MyClass(take(x, ""), take(y));
	}
}

class MyClass {
	public val x: unique string;
	public val y: unique string;
	
	public unique this(x: unique string, y: unique string) {
		this.x = x;
		this.y = y;
	}
}
```

## Automatic conversion of unique values

Unique values can be converted to regular values, and they do so automatically whenever needed:

```
class MyObject {
	unique this() { ... }
}

foo(object: &MyObject) {
	...
}

bar(object: MyObject) {
	...
}

consume(object: unique MyObject) {
	...
}

val a = new MyObject(); // type of a is unique MyObject
foo(a); // OK, can borrow unique object
bar(a); // from now on, type a is simply MyObject
bar(a);
```

In fact, the default no-parameter constructor will return a unique value - and if moved, 

## Weak references

When using destructible values, or when working in a system without garbage collector, we have to make sure no reference loops exist, otherwise a memory leak may occur. These can be solved with weak references.

Weak references must be locked before they can be used, and locking them will result in null if the reference value has been destructed.

```
class Node {
	val name: string;
	var parent: weak Node?;
	val children: Node[];
	
	this(name: string, children: Node[]) {
		this.name = name;
		this.children = children;
		
		for child in children:
			child.parent = this;
	}
	
	get parentName: string? {
		lock parent {
			return parent ? parent.name : null;
		}
	}
}
```

Lock statements exist in two variants:

```
lock fieldname {
	// object accessible with the same name as its field
	// do something with fieldname
}
```

## Borrow with this lifetime

It is also possible to borrow to this, thus the following is possible:

```
class OtherClass {
	var name: &string;
	
	unique this() {
		name = "x";
	}
	
	setName(value: &this string) {
		name = value; // OK
	}
}

val a = new OtherClass(); // create a unique value (important for lifetime analysis)
val b = "y";
a.setName(b);
```

In the latter case, the value must remain valid for as long as this exists.

Borrowed values marked as &this use compile-time lifetime analysis to ensure they don't outlast the value they are stored in:

```
val a = new OtherClass();
{
	val b = "y";
	a.setName(b); // error: a may outlive b, thus this assignment is invalid
	a.setName("z"); // OK, due to "z" being a static string, which can live forever
	a.setName(":" + b); // error, the dynamically allocated result of the sum will only last for the duration of the statement
}
```
