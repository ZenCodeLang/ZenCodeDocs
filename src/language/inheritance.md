# Inheritance

Classes may inherit other classes and implement interfaces. This document describes how inheritance is implemented in ZenCode.

In ZenCode, inheritance should be used sparingly. If your intended functionality can be reasonably implemented using interfaces, by all means, do so. Class inheritance should generally only be used for a hierarchy of components which conforms the following guidelines:

- The superclass and its subclasses are written by the same team.
- The subclasses are quite similar, but their differences in implementation cannot be (easily) implemented using interfaces.

## Virtual classes

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

## Virtual methods

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

## Subclass constructors

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

## Abstract classes and methods

Classes can also be declared `abstract`, meaning that they cannot be instantiated, they *must* be extended.

```
abstract class Foo {
	virtual act() {
		print("Hello");
	}
}

class Bar : Foo {
	override act() {
		print("Yo");
	}
}

val a = new Foo(); // error: cannot instantiate an abstract class
val b = new Bar(); // OK
```

`abstract` implies `virtual`, and so it is not necessary to declare classes as being both.

Methods can be declared `abstract` as well. Abstract methods have no implementation - they must be implemented by a subclass. If a class has abstract methods, the class *must* be explicitly declared abstract as well.

```
abstract class Bar {
	abstract act(): void;
}

class Foo : Bar {
	override act() {
		print("Yo");
	}
}
```

A non-abstract subclass is required to implement every abstract method on its superclass. If a subclass is abstract, it is not required to do so; but any unimplemented abstract superclass methods will be inherited as well, and will still need to be implemented by any non-abstract subclass.