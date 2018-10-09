# About ZenCode

ZenCode is a programming language designed to address various challenges in modern-day software development. It intends to provide software developers with a modern language, allowing them to write readable and reliable code for a wide variety of uses.

## Designed to be transpiled

Very often, we have little choice in the system we are writing for. If you need an Android application, you'll be writing Java; and if you're programming for iOS, you'll be stuck with Swift. On the browser, it's Javascript, and even in other systems, you may be restricted by the system you are integrating with.

This means that code written for one system cannot be used on the other. Some transpilation tools exist, but none of these languages or systems were designed to be used in such a way. It may work - but it's far from perfect.

ZenCode, instead, is designed from day one to be transpiled. In fact, as of writing, a native compiler doesn't even exist (although one will certainly be created eventually). You write code in ZenCode, and depending on your target, you can compile to Java or C# bytecode, Javascript or even readable *source code*.

Even the standard libraries are broken into small modules, allowing projects to include only what they need. This prevents the need to include a large runtime library just to support programming with ZenCode. This makes it particularly suitable for mobile or web applications where package size is important.

## Designed to be safe

Applications can load ZenCode modules and scripts specifying exactly which classes and libraries they are allowed to use. Anything that is not explicitly allowed is blocked. Attempting to use invalid classes or methods will cause a validation error as soon as the module or script is loaded. This allows developers to load scripts or modules from unknown sources with the peace of mind that they will not access resources they are not allowed to. (although they could still consume more memory or processor power than they should; can't do much about that)

ZenCode doesn't support reflection nor any of the problems it usually represents. Private fields cannot be accessed. Final fields cannot be modified. Access checks are enforced, always. Random pointer access is not possible. Constness cannot be circumvented. Immutable is forever.

In combination with an easy API to load and unload scripts or modules at runtime, this makes it very practical to use ZenCode as scripting or plugin development language, even inside systems not programmed in ZenCode: the code will be translated to whatever language or system the parent process is running, allowing these scripts and modules to load with virtually no overhead. No additional virtual machine or interpreter is involved.

## Designed to be robust

Additional language features help to guarantee both security and stability: constness and immutability are enforced and annotations can be used to enforce invariants on methods, fields and classes. Fields are always private and can only be exposed through getters and setters.

Values cannot be null unless specified otherwise. You can't accidentally pass a null value where one wouldn't be expected - it will error right at the location where the null was passed and not sometime later. This can save a lot of debugging time.

Likewise, values can be destructed in a deterministic manner, even if the underlying system is using a garbage collector. Files will be closed, managed resources will be cleaned up, and you don't have to break your head for it - things work by default. RAII is a perfectly viable pattern in ZenCode.
