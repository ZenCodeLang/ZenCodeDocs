# ZenCode 3.0 Extensions

[//]: # (TODO WIT: Difference between Tuple and Class? Immutability and Extensibility I presume?)

[//]: # (Also, has this changed?)

## Structs

It is now possible to define structs, which are passed by value:

```
struct PointF {
	var x: float;
	var y: float;
	
	this(x: float, y: float) {
		this.x = x;
		this.y = y;
	}
}

modify(point: PointF) {
	point.x = 2;
}

var a = new PointF(1, 1);
modify(a);
println("x: " + a.x); // will print "x: 1"
```

Just like classes, structs can have methods, getters, settings, or may even implement interfaces.

When a struct is passed borrowed, it is passed by reference instead:

```
modify2(point: &PointF) {
	point.x = 2;
}

var a = new PointF(1, 1);
modify(a);
println("x: " + a.x); // will print "x: 2"
```

### Struct declaration

Structs define value types. They are similar to classes, except they have value semantics instead of object semantics.
That is, in the following example, the function will not modify the value that was passed in:

```
struct Point {
	var x: number;
	var y: number;
}
function doSomething(p: Point) {
	p.x = 20;
}

val a as Point = { 10, 10 };
doSomething(a);
print(a.x); // will print 10
```

```Railroad
Sequence(
    'struct',
    NonTerminal('Identifier'),
    Optional(NonTerminal('GenericParameters')),
    Optional(Sequence(':', NonTerminal('Type'))),
    '{',
    ZeroOrMore(NonTerminal('DeclarationMember')),
    '}'
)
```

## Mutable borrowing

Borrows can be declared mutable, which makes the val fields modifyable:

```
class MyObject {
	val _name: string;
	
	this(name: string) {
		_name = name;
	}
	
	get name => _name;
	
	&mut set name {
		_name = name; // OK due to the &mut
	}
}

function modify(object: &MyObject) {
	object.name = "y";
}

var a: mut MyObject = new MyObject("x");
modify(a);
println("Name: " + a.name); // prints "Name: y"
```

## Multithreaded classes and interfaces

Classes and interfaces can be declared multithreaded. Multithreaded objects can be shared between multiple threads but must obey additional language rules. These rules help to ensure that multithreading is implemented without nasty surprises. Most particularly, they guarantee that no language invariants are broken while still providing good performance.

Als fields in a multithreaded object must themselves be multithreaded objects or struct values. All primitive types are multithreaded. Additionally, in multithreaded objects, it is not permitted to modify var fields directly, they must be locked instead before modification. Two exceptions exist to this rule: mutably borrowed objects can be modified directly, and so can objects that are not yet fully constructed:

```
multithreaded class MyObject {
	var _name: unique string;
	
	this(name: unique string) {
		_name = name; // allowed
	}
	
	&mut setMutName(name: unique string) {
		_name = name; // allowed due to the mutable borrow of this
	}
	
	set name {
		lock _name as name {
			name = $;
		}
	}
}

var a = new MyObject("x");
a.name = "y";
```

If all fields in a class are final (val), and each of those fields are multithreaded themselves, the class automatically becomes multithreaded as well.

Likewise, interfaces can be marked as multithreaded. Although classes may always implement a multithreaded interface, an object can only be casted to a multithreaded interface if it is an instance of a multithreaded class. (borrowing to a multithreaded interface, on the other hand, is always permitted)

It is possible for a non-multithreaded class to extend a multithreaded class. On the other hand, a multithreaded class cannot extend a non-multithreaded class.

## Sharing objects between threads

Objects can be made shared, allowing them to be shared between threads. It is possible either construct objects shared (using a constructor marked `shared`) or to convert it from a `unique` value. Objects not explicitly tagged with `unique` or `shared` cannot be turned into shared objects, and `shared` can only be used on `multithreaded` objects.

```
var a = new MyObject("x");
startThread(() => {
	println("Thread a: " + a.name);
});
startThread(() => {
	println("Thread b: " + a.name);
});

multithreaded class Bar {
	val name: shared string;
	
	public shared this(name: shared string) {
		this.name = name;
	}
}
var a = new Bar("x");
startThread(() => {
	println("Thread a: " + a.name);
});
```

In a multithreaded object, it is a good idea to group related fields together, so that only one lock is necessary to mutate the fields:

```
multithreaded class NotSoGoodObject {
	var x: double;
	var y: double;
	var z: double;
	
	this(x: double, y: double, z: double) {
		this.x = x;
		this.y = y;
		this.z = z;
	}
	
	&multiply(scale: double) {
		lock x {
			x *= scale;
		}
		lock y {
			y *= scale;
		}
		lock z {
			z *= scale;
		}
	}
}

// automatically multithreaded due to all fields being final
class SharedState {
	val x: double;
	val y: double;
	val z: double;
	
	this(x: double, y: double, z: double) {
		this.x = x;
		this.y = y;
		this.z = z;
	}
	
	&mut multiply(scale: double) {
		// permitted due to the mutable borrow
		x *= scale;
		y *= scale;
		z *= scale;
	}
}

multithreaded class BetterObject {
	var state: unique SharedState;
	
	this(x: double, y: double, z: double) {
		state = new SharedState(x, y, z);
	}
	
	&multiply(scale: double) {
		lock state {
			// the lock results in a mutably borrowed value, thus the mutable borrow method can be used
			// note that this would not work if state were a shared object, as shared objects cannot be borrowed mutably
			state.multiply(scale);
		}
	}
}
```

## Moving objects to different threads

Certain values can be moved to different threads:

- Shared values of a multithreaded type can be trivially moved to other threads
- Primitive values, including strings, can be moved to other threads
- Values marked unique can be moved to different threads unless they are threadlocked (see below)

For instance, the following is permitted:

```
// not marked multithreaded
class SimpleObject {
	public val name: string;
	
	unique this(name: string) {
		this.name = name;
	}
}

var a = new SimpleObject();
startThread(() => {
	println("Name: " + a.name);
});
```

Note that borrowed values can never be transferred between threads, since there is no way to validate lifetime for such objects.

## Thread-locked values, classes and interfaces

In a given runtime environment, the host may need to expose values - usually containing native handles of some sort - which are not thread-safe and thus not meant to be transferred to be safe. Such values are called "thread-locked". In extent, any class containing thread-locked values will also become thread-locked.

Interfaces may be declared to be thread-locked using the `threadlocked` modifier. If a class is threadlocked, it cannot be casted into a non-threadlocked interface. (it can still be borrowed to such interface, though, since borrowed values cannot be transferred between threads)

## Handling of strings

Due to their ubiquity and due to different handling of strings between different implementations, strings have special handling and can be converted between regular values, `unique` and `shared` freely. Depending on the target system, this could be a no-op, a simple reference conversion or a full string duplication.

Most particular, in reference counted systems, conversion of `unique` to regular or `shared` is free, but conversion between regular and `shared` will usually result in string duplication. Likewise, conversion between regular or `shared` and `unique` will generally also duplicate the string. This should be kept in mind when performing such conversions.

In garbage-collected systems, such conversions are usually no-ops.

Borrowing can be assumed to always be free, and should never incur any overhead.
