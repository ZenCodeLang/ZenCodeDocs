# Inheritance

Classes may inherit other classes and implement interfaces. This document describes how inheritance is implemented in ZenCode.

In ZenCode, inheritance should be used sparingly. If your intended functionality can be reasonably implemented using interfaces, by all means, do so. Class inheritance should generally only be used for a hierarchy of components which conforms the following guidelines:

- The superclass and its subclasses are written by the same team.
- The subclasses are quite similar, but their differences in implementation cannot be (easily) implemented using interfaces.

ZenCode is written with this principle in mind - it assumes you *won't* be using inheritance. By default, classes cannot extend other classes unless marked `virtual`:

```
class Foo {
}

class Bar : Foo {  // error: Foo is not virtual
}

virtual class A {
}

class B : A { // OK
}

class C : B { // error: B is not virtual
}
```

Likewise, methods cannot be overridden unless they are also marked `virtual`, and the overriding method must be marked as such with `override`:

```
virtual class Foo {
	virtual act() {
		print("Hello");
	}
}

class Bar : Foo {
	override act() {
		print("Sleeping");
	}
}
```

If a method is marked as `override`, it **must** override a method, otherwise it **must not**. Additionally, it is an error for a class to have two identical methods; so the following is not permitted:

```
virtual class Foo {
	virtual act() {
		print("Hello");
	}
}

class Bar : Foo {
	act() { // error: there's already an identical method act
		print("Sleeping");
	}
}
```

Every subclass constructor is required to call a superclass constructor, unless a no-argument superclass constructor exists:

```
virtual class Foo {
	val name: string;
	
	this(name: string) {
		this.name = name;
	}
}

class Bar1 : Foo {
	// error: default constructor missing while superclass has no no-args constructor
}

class Bar2 : Foo {
	this() {
		// error: not calling superclass constructor
		print("Constructing Bar2");
	}
}

class Bar3 : Foo {
	this() {
		super("Bert"); // OK
	}
}
```

