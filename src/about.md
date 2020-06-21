# About ZenCode

ZenCode is a programming language intended to be used as scripting language within a larger host application. Thus if you have an application and are looking for a way to safely integrate plugins or user-provided scripts, ZenCode may be for you.

What is it?

- A safe system, fully controlled by its host environment. The host application has fine control over which functions the scripts may perform.
- It is intended to be compiled on the fly, and in such a manner that communication between the scripts and the host application has minimal or no overhead. Object wrapping and defensive copying is rarely necessary.
- A modern and practical programming language
- Accompanied by modern and practical programming tools
- Strongly typed, with no built-in possibility to "cheat the system"

What is it not?

- a systems programming language
- The language with the ultimate performance. Although performance is considered as important, security and ease of use are far more important.
- Although it is possible to create a runtime system to allow you to create standalone scripts or application, it is not its main intended use.

ZenCode is created out of dissatisfaction with the scripting languages that are available today. Amongst the languages used, only few can be effectively and easily used as languages for plugins and scripts in my own applications. Javascript, Java and Lua are the most meaningful candidates here, yet I found them hard to use effectively in practice, for a variety of reasons:

- Data encoded within the virtual machines or runtime environments is usually encoded in a completely different way than the target system, resulting in a lot of work as well as high overhead for these systems to communicate with each other.
- Most scripting lanugages are not statically typed. Although this results in less code to be typed on the short term, it also results in confusion in more complex codebases.
- Sometimes it can be hard to control with functionality is available to the scripts, opening up security issues if untrusted code is executed.
- Debugging capabilities of the host system are usually limited, if not completely absent.

ZenCode attempts to address these issues by defining a strongly typed programming language with sufficient flexibility so that it allows to integrate very tightly with its host system. It makes minimal assumptions about the system it runs in, (for instance, it does not assume the existence of a garbage collector), its standard library does not have any functionality to interact with the operating system (no file I/O, for instance) and it provides the host system with a wide range of features to make the life of the scripter as easy as possible:

- The host system can define a set of symbols to be exposed as global variables
- The host system defines a set of libraries which can be imported by scripts; it may even use scripts as modules that can be imported in other scripts
- The host system can also the define so-called "bracket expressions". These start with the '&lt;' character and it is completely up to the host how to parse them. For instance, in CraftTweaker, expressions such as &lt;item:minecraft:diamond&;gt; are used to refer to items, which is a very common operation. More complex bracket parsers could make it possible to, for instance, define XML expressions or React-like user interface definitions.
- The language also defines if values passed to scripts are immutable and if the called function is allowed to hold onto them after the function returns. This reduces the number of heap allocated objects and defensive copies to be made.

## Designed to be transpiled

Very often, we have little choice in the system we are writing for. If you need an Android application, you'll be writing Java; and if you're programming for iOS, you'll be stuck with Swift. On the browser, it's Javascript, and even in other systems, you may be restricted by the system you are integrating with.

ZenCode, instead, is designed from day one to be transpiled. In fact, as of writing, a native compiler doesn't even exist. You write code in ZenCode, and depending on your target, you can compile to Java or C# bytecode.

Even the standard libraries are broken into small modules, allowing projects to include only what they need. This prevents the need to include a large runtime library just to support programming with ZenCode. This makes it particularly suitable for mobile or web applications where package size is important.

## Designed to be safe

Applications can load ZenCode modules and scripts specifying exactly which classes and libraries they are allowed to use. Anything that is not explicitly allowed is blocked. Attempting to use invalid classes or methods will cause a validation error as soon as the module or script is loaded. This allows developers to load scripts or modules from unknown sources with the peace of mind that they will not access resources they are not allowed to. (although they could still consume more memory or processor power than they should, at least they cannot do any permanent harm to the system)

ZenCode doesn't support reflection nor any of the problems it usually represents. Private fields cannot be accessed. Final fields cannot be modified. Access checks are enforced, always. Random pointer access is not possible. Constness cannot be circumvented. Immutable is forever.

In combination with an easy API to load and unload scripts or modules at runtime, this makes it very practical to use ZenCode as scripting or plugin development language, even inside systems not programmed in ZenCode: the code will be translated to whatever language or system the parent process is running, allowing these scripts and modules to load with virtually no overhead. No additional virtual machine or interpreter is involved.

## Designed to be robust

Additional language features help to guarantee both security and stability: constness and immutability are enforced and cannot be circumvented. Fields are always private and can only be exposed through getters and setters.

Values cannot be null unless specified otherwise. You can't accidentally pass a null value where one wouldn't be expected - it will error right at the location where the null was passed and not sometime later. This can save a lot of debugging time.

Likewise, values can be destructed in a deterministic manner, even if the underlying system is using a garbage collector. Files will be closed, managed resources will be cleaned up, and you don't have to break your head for it - things work by default. RAII is a perfectly viable pattern in ZenCode.
