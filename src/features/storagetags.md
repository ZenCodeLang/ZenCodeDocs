# Memory Management

ZenCode allows developers to specify if a certain object is mutable or immutable as well as value ownership through a feature called storage tags. Storage tags are part of an object's type. Whereas the type specifies what a value contains, storage tags specify how and where it can be used. Is there a single owner or multiple? Can this object be stored or is it only available for temporary use? Can it be modified? Can it be used in a multithreaded context? Storage tags define all of these properties with a simple annotation tag.

By default, ownership is shared and everything is mutable, but being able to specify restrictions allows for more reliable behavior, improved system security and increased performance.

Storage tags can be added to types and methods with a backtick: (in this example, the `unique` and `borrow`)

```
class MyClass {
    myFunc`borrow(a as int) as void { ... }
}

function doSomething(object as MyClass`borrow) {
    object.myFunc();
}

var instance = new MyClass`unique();
doSomething(instance);
```

In order to implement proper memory management, the system needs to know whether a value is still in use or not. This is where ownership comes in: when a value is allocated, it is owned. This ownership can then be passed on or distributed amongst multiple locations. If there are no more owners, it is safe to clean up the object and its memory. In the case of a destructible value, the system guarantees that it its destructor is called immediately. Whether and when the memory is reclaimed is up to the system: in a reference counted system, it will be reclaimed immediately; in a garbage collected system, it is up to the garbage collector.

Objects can also be passed without passing ownership: in this case the code has to prove that the object is used for no longer than granted and that there will always be an owner for as long as the object is "lend out". This system is called borrowing. (and for those who know Rust, the  borrow checker in ZenCode is highly similar) This helps to improve performance, since these borrowed references don't need to be counted - their validity is verified at compile time.

Aside from specifying ownership, storage tags can also be used to specify if a value is modifyable, not modifyable (const) or immutable. Both always come together.

The following storage tags exist by default:

- auto
- const
- immutable
- multithreaded
- unique
- static
- borrow
- mutable

## Auto and static

By default, the auto tag is used, meaning that ownership is shared and the value is mutable (modifyable). This allows code to "just work", but it is also the least restrictive and least performant (and also the perfect way to shoot yourself in the foot in a multithreaded system).

Values that are allocated once and then kept for the remainder of program execution are not marked auto; they are automatically marked `static` instead. This is true for constants, enum values and strings. Since a `static` value can be cast to an `auto` value, this fact usually goes unnoticed.

## Unique

Auto allows for shared ownership, making it possible to keep the value in multiple places (borrowing aside). In systems without garbage collector, or when storing destructible values, this comes with an overhead: the number of pointers to the object needs to be counted. This means additional processor time and storage to keep track of these counts.

Quite often, a value only needs a single owner. (especially when borrowing, as will be explained later) In this case, an object can be marked as such. This unique value can be passed to other places but cannot be stored multiple times.

If such a value is moved around, the old value will become invalid and can no longer be used. (This mechanism is called move semantics). This is illustrated with the following code, which would not compile:

```
class MyClass {
    foo`unique() as void {}
}

val a = new MyClass`unique();
val b = a;
b.foo(); // OK
a.foo(); // error: value was moved
```

## Method storage tags

The example above also shows something new: a storage tag was added to the `foo()` method.

In a class method, what is the storage tag assigned to `this`? By default, `auto` is assumed. This works if we call the method on an `auto` tagged value, but this would not work in the case of a `unique` tagged value: `unique` is not compatible with `auto`.

To fix this problem, we can tell a method that it is intended to operate on a value tagged with a specific tag - in our example, `unique`. This method would then no longer be usable on an `auto` tagged value, however.

## Borrowing

Quite often, we need to pass a value without passing ownership. This is the case for values that are only "lend out" temporarily. We can do so through a mechanism called borrowing.

Values can be tagged `borrow` to indicate that it can be used temporarily. Three types of borrows exists:

- Borrowing until the end of scope. This can be used to borrow values for the duration of a method call. This is the default
- Borrowing for the duration of the current object. This allows the value to be stored in a field of the current object. This can be indicated with `borrow:this`.
- Borrowing a parent object. This is similar to `borrow:this` except that the value is not usable during initial construction and final destruction. This allows a child object to maintain a reference to a parent without the risk of accessing an incomplete object.

```
class MyClass {
    var other as MyClass`borrow:this?;
    
    this(other as MyClass`borrow:this?) {
        this.other = other;
    }
    
    foo(value as MyClass`borrow) {
        this.other = value; // error: incompatible scope
    }
    
    bar(value as MyClass`borrow) as MyClass {
        val tmp = new MyClass(value); // OK
        return tmp; // error: tmp scope limited by value scope
    }
}

val a = new MyClass`unique(null);
val b = new MyClass`unique(a);
b.foo(a);
```

In the example above, foo and bar will fail to compile. Foo will fail because the value can only be kept for the duration of the method call, and thus cannot be stored in the current object. Bar will fail because the passed value is stored in tmp, and returning tmp from the method violates the requirement that value is not kept for longer than the method call (it would be kept in the returned value).

Borrow also has a second side-effect: it makes the value immutable for the duration of the borrow. Thus the following is not possible:

```
class MyClass {
    var name as string : get, set;
    
    this(name as string) {
        this.name = name;
    }
}

val a = new MyClass`unique("X");
a.name = "foo"; // OK
{
    val b = a as MyClass`borrow; // OK
    b.name = "Y"; // error: b is immutable
    a.name = "Z"; // error: a is borrowed as immutable
}
a.name = "Bar"; // OK
```

In this example, neither a nor b can be modified for as long as b exists.

Sometimes having a value borrowed as immutable is not desired behavior. You may need to pass an object to a function and explicitly allow that function to modify the value as well. This can be performed with the `mutable` storage tag. Its operation is similar to `borrow` except that the value can be modified.

Likewise, whereas the modification of auto is always allowed, const can be used as well. The semantics are the same but a const cannot be modified (note however that this is not an immutable value; as it may still be modified through a non-const pointer).

An immutable variant exists too. This value can be owned  at multiple locations, but none of them can modify it.

## Local

A special storage tag exists called `local` which is similar to `unique` except that ownership (and thus also the value) cannot be moved.

Local, being more restrictive than unique, allows for low-level compilers to perform even more aggressive optimizations, including the ability to store a value on the stack or inline in an enclosing object. This can decrease the number of allocations.

## Multithreading

Not all storage types can be used safely in a multithreaded environment. Most particularly, `auto` and `const` tagged items are single-threaded.

`immutable` values are safe to use between threads. Borrowed values cannot cross thread boundaries; however, an immutable object can be borrowed from in multiple threads independently.

In order to support multithreaded mutable values, the `multithreaded` tag can be used. These can be shared amongst threads, but methods have to be implemented carefully.

## Storage conversions

Certain conversions are possible, often with their own side-effects:

- unique and static can be cast to auto and immutable. For a unique value, this counts as a move operation, making the original value invalid.
- unique can also be cast to multithreaded
- anything can be borrowed as borrow, as long as there are no mutable references. (TODO: borrowing an `auto` or `multithreaded` value means immutability cannot be guaranteed on such values. Is this acceptable?)
- unique and auto can be borrowed as mutable
- auto can be cast to const

Storage conversions can in many cases also be used to allow functions and methods to work on more than one type of object. For instance, a method tagged `borrow` would work on any kind of object; however, it would also be more restricted in what it can do with the object.

Note that some special rules apply to such conversions as well:

Note that converting a unique value to auto, immutable or multithreaded this way will render the original value invalid. If the resulting value isn't stored or returned, it will be destructed.

Likewise, calling a method tagged `unique` will pass ownership of the target object to the calling function as well. If this is undesired, use `borrow` or `mutable` instead.

## Overview of storage tag properties

| Tag           | Mutability | Multithreading | Ownership |
|---------------|-----------|----------------|----------|
| auto          | mutable    | singlethreaded | shared |
| const         | const      | singlethreaded | shared |
| immutable     | immutable  | multithreaded | shared |
| multithreaded | mutable   | multithreaded | shared |
| unique        | mutable   | singlethreaded | single, movable |
| static        | immutable | multithreaded | shared |
| borrow        | const* | singlethreaded | none |
| mutable       | mutable   | singlethreaded | none |
| local        | mutable | singlethreaded | single, nonmovable |

\* immutable unless borrowed from `auto` or `multithreaded`