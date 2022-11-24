# ZenCode Language Specification

## Introduction

The ZenCode programming language is a general purpose programming language focused on the capability of being translated to various systems. This allows code to be written once and then used on a wide variety of platforms, including web (javascript), mobile (Android / iOS) and servers, with the ability for 3rd parties to write their own backend compiler. It is a high-level language and is focused on getting the job done efficiently. Although performance is considered important, clarity of coding has a higher priority: it is indended to be a practical language, easy to read and write, and easy to understand.

ZenCode can be used both as scripting language as well as module programming language, both with slightly different variations.

## Compilation stages

ZenCode is compiled in a modular fashion. Multiple source files can be compiled into a module. This module may itself depend on other modules. Multiple modules can be compiled into a single target-dependant binary file.

A module is compiled in various stages:

- Parsing: all source files in the module are parsed into a syntax tree
- Semantic analysis: the syntax trees of the source files are processed to build symbol tables, declare variables, link type references to their definitions and in general determine the meaning of the program
- Normalization: the semantic model of the module is converted to a form that is easier to process by subsequent compilation stages
- High-level optimization: target-indepedent optimizations are performed to improve performance of the output (this stage is optional)
- Target-dependent analysis: the target compiler analyzes the modules to be compiled, in order to determine how it the language elements will be compiled to the target system
- Target-dependent optimization: depending on the target compiler, additional optimizations may be performed
- Target-dependent code generation: the target compiler generates code

The target-dependent steps may vary and depend entirely on the target compiler; developers are free to build their own target compiler as desired.

## Lexical grammar

Each source file is interpreted as UTF-8 encoded file without Byte Order Mark (BOM). The lexical analyzer splits this source file into tokens.

Token types are specified by their respective regular expression. Two kinds of tokens exists: whitespace and non-whitespace tokens. Whitespace tokens are omitted during parsing but can be preserved separately (eg. to execute script instructions or to preserve comments and documentation components).

### Whitespace tokens

The following whitespace token types exist:

- Preprocessor instructions: ```#[^\n]*[\n\\e]```
- Single-line comment: ```//[^\n]*```
- Multi-line comment: ```/\\*([^\\*]|(\\*+([^\\*/])))*\\*+/```
- Whitespace: ```( |\t|\r|\n)```

Preprocessor instructions are treated as whitespace by the ZenCode compiler, but target environments may choose to process them. It is up to the target environment to choose how these are processed, the ZenCode language itself does not assign any meaning to these comments. Preprocessor comments starting with a double hash (## something) and an exclamation mark (#! something) are reserved for future ZenCode processing. Additionally, if a file starts with a comment #! it will be guaranteed to be ignored in any future versions of ZenCode (thus can be safely used to indicate the program to execute the script).

Preprocessor instructions, although treated as whitespace by the ZenCode compiler, should also only be used for preprocessors and not for comments. Using # for comments may result in undefined behavior.

Whitespace is generally ignored, though it can have a meaning inside bracket expressions and custom parsers.

### Non-whitespace tokens

The following non-whitespace token types exist:

- Identifier: ```@?[a-zA-Z_][a-zA-Z_0-9]*```
- Local identifier: ```$[a-zA-Z_][a-zA-Z_0-9]*```
- Floating-point constant: ```\-?(0|[1-9][0-9_]*)\.[0-9][0-9_]*([eE][\+\-]?[0-9_]+)?[a-df-zA-DF-Z][a-zA-Z_]*```
- Integer constant: ```\-?(0|[1-9][0-9_]*)[a-zA-Z_]*```
- Integer constant with prefix: ```\-?(0b|0x|0o|0B|0X|0O)(0|[1-9a-fA-F][0-9a-fA-F_]*)[a-zA-Z_]*```
- Single-quoted string: ```'([^'\\\n]|\\(['"\\/bfnrt&]|u[0-9a-fA-F]{4}))*'```
- Single-quoted wysiwyg string: ```@'[^']*'```
- Double-quoted string: ```"([^"\\\n]|\\(['"\\/bfnrt&]|u[0-9a-fA-F]{4}))*"```
- Double-quoted wysiwyg string: ```@"[^"]*"```
- Brackets: one of ```{ } [ ] ( )```
- Operators: one of ```. .. ... , + += ++ - -= -- ~ ~= * *= / /= % %= | |= || & &= && ^ ^= ? ?. ?? : ; < <= << <<= > >= >> >>= >>> >>>= => = == === ! != !== $ ` ```

Integers and floating-point numbers may also have a suffix. The suffix may be one of the standard suffixes ('u', 'U', 'ul', 'UL', 'f', 'd') or a custom suffix. (see later for more information about custom suffixes)

Integers may also be prefixed with a base:

- 0b or 0B: binary
- 0o or 0O: octal
- 0x or 0X: hexadecimal

Additionally, integers and floating-point numbers may contain the _ character. These characters are ignored and can be used as separator to make long numbers more readable. Numbers cannot start with the _ character and neither can the digits after the comma. Thus the following are not valid numbers:

```
_1 (will be interpreted as an identifier)
1._2 (will be interpreted as 3 tokens, '1', '.', '_2')
```

However, the following are valid numbers:
```
0xDEAD_BEEF
100_000
1.234_567
100_000_ // OK, may end with underscore
```

Inside strings, escape sequences may be used. The following escape sequences exist in both single-quoted and double-quoted strings:

- ```\b``` (backspace)
- ```\f``` (line feed)
- ```\n``` (newline)
- ```\r``` (carriage return)
- ```\t``` (tab)
- ```\u[0-9a-fA-F]{4}``` (unicode character 0 - 0xFFFF)
- ```\U[0-9a-fA-F]{6}``` (unicode character 0 - 0xFF_FFFF)
- ```\&{named-character};``` for a named character

Named characters such as ```\&copy;``` or ```\&reg;``` are supported and make it easy to read and write commonly used special characters. The full list of named characters can be found [here](namedcharacters.html).

Strings and identifiers may be prefered by the @ character. An identifier prefixed by @ is indentical by the identifier without the prefix, with the only difference that they are not processed as keywords. Thus a variable that should be named "final" can then be named "@final" to prevent it from being interpreted as the final keyword. (this is also the recommended way to use variables which would be named as keywords, so don't precede or suffix them with underscores or anything like it...

The "$" identifier is special and has two possible meanings:

- When indexing an array, $ is set to the length of the array. This makes it easy to access the last (or nth last) element in an array: `myArray[$ - 1]`
- In a setter, $ specifies the value that is currently being set:

```
class MyClass {
	var _test: int;
	
	public set test {
		_test = $;
	}
}
```

In case both may be applicable, the innermost definition will be used.

Identifiers starting with $ are reserved for future use.

A string literal prefixed by the @ character is interpreted as wysiwyg string. In such string, escape characters are not processed, but the ' or " character cannot occur. Also, these strings may span multiple lines.

For instance, the following wysiwyg strings are valid examples:

```
@"C:\Program Files\MyApplication"
@"INSERT INTO entities (key, value)
  VALUES (%1, %2)"
```

Certain identifiers are reserved as keywords. The following keywords are specified:

```
abstract
alias
as
bool
break
byte
case
catch
char
class
const
continue
default
do
double
else
enum
expand
extern
export
false
finally
float
for
function
get
if
in
implements
implicit
import
int
interface
internal
is
lock
long
match
multithreaded
mut
new
null
override
panic
private
protected
public
return
sbyte
set
short
static
string
struct
super
switch
this
throw
throws
true
try
uint
ulong
ushort
usize
val
var
variant
virtual
void
weak
while
```

## File grammar

A file may consist of one or more imports, zero or more declarations and zero or more statements. An empty file is a valid source file.

```Railroad
Sequence(
    ZeroOrMore(NonTerminal('Import')),
    ZeroOrMore(Choice(0, NonTerminal('Definition'), NonTerminal('Statement')))
)
```

Imports always import a single definition from a given package, and can optionally be renamed:

```Railroad
Sequence('import', Optional('.'), NonTerminal('Identifier'), ZeroOrMore(Sequence(',', NonTerminal('Identifier'))), Optional(Sequence('as', NonTerminal('Identifier'))), ';')
```

If an import starts with a '.', it defines an import in the current module. It is also the only way to import a definition
from another package in the same module.

## Declarations

A declaration can be a class, interface, struct, enum, variant or function . Although it is recommended to have a single
declaration per file and to give the file the exact same name as its declaration, it is not required to do so.

```Railroad
Sequence(
    ZeroOrMore(NonTerminal('Annotation')),
    ZeroOrMore(Choice(0,
        'public',
        'private',
        'internal',
        'extern',
        'abstract',
        'final',
        'protected',
        'implicit',
        'virtual'
    )),
    Choice(0,
        NonTerminal('ClassDeclaration'),
        NonTerminal('InterfaceDeclaration'),
        NonTerminal('EnumDeclaration'),
        NonTerminal('AliasDeclaration'),
        NonTerminal('FunctionDeclaration'),
        NonTerminal('ExpansionDeclaration'),
        NonTerminal('VariantDeclaration')
    )
)
```

### Class declaration

Classes are reference types and may contain fields and any number of definition members.

Classes may extend a single superclass, but they don't have to.

```Railroad
Sequence(
    'class',
    NonTerminal('Identifier'),
    Optional(NonTerminal('GenericParameters')),
    Optional(Sequence(':', NonTerminal('Type'))),
    '{',
    ZeroOrMore(NonTerminal('DeclarationMember')),
    '}'
)
```

### Interface declaration

Interfaces are reference types and may contain any number of definition members. Members don't need implementations and are always assumed to be abstract. An implementation may be given for definition members, in which case it acts as default implementation; and they may also be declared final, in which case it cannot be implemented or overridden by implementations.

```Railroad
Sequence(
    'interface',
    NonTerminal('Identifier'),
    Optional(NonTerminal('GenericParameters')),
    Optional(Sequence(':', NonTerminal('Type'), ZeroOrMore(Sequence(',', NonTerminal('Type'))))),
    '{',
    ZeroOrMore(NonTerminal('DeclarationMember')),
    '}'
)
```

### Enum declaration

Enums define a closed set of possible values. Two kinds of enums exist: object enums and value enums. Object enums are defined as a series of possible object values, whereas value enums define a possible set of values:

```Railroad
Sequence(
	'enum',
	NonTerminal('Identifier'),
	Optional(Sequence(':', NonTerminal('Type'))),
	'{',
	Optional(Sequence(NonTerminal('EnumValue'), ZeroOrMore(Sequence(',', NonTerminal('EnumValue'))), Optional(','))),
	Optional(Sequence(';', ZeroOrMore(NonTerminal('DeclarationMember')))),
	'}'
)
```

### Alias declaration

Type aliases can be used to create alternative names for types. The types are considered equivalent.

Type aliases are mostly useful in the following scenarios:

- When libraries need to re-export types from other libraries
- To create aliases to generic types with specific type parameters

```Railroad
Sequence(
	'alias',
	NonTerminal('Identifier'),
    Optional(NonTerminal('GenericParameters')),
	NonTerminal('Type'),
	';'
)
```

### Function declaration

Function definitions can be used to define functions which do not exist within the context of a surrounding class.
They are mostly useful to define utility functions or helper functions inside scripts.

```Railroad
Sequence(
	'function',
	NonTerminal('Identifier'),
	NonTerminal('FunctionHeader'),
	NonTerminal('FunctionBody')
)
```

### Expansion declaration

Expansions can add type members (and interface implementations) to existing types. This makes it possible to add members to types even in other libraries.
Expansions can be defined in libraries as well and will be available to any module that defines the expanding libraries as dependency.

```Railroad
Sequence(
	'expand',
    Optional(NonTerminal('GenericParameters')),
	NonTerminal('Type'),
	'{',
    ZeroOrMore(NonTerminal('DeclarationMember')),
	'}',
)
```

### Variant declaration

Variants are typed unions - that is, they are a collection of possible types, each of which may have its own set of fields.
Variants are very useful in combination with match operators and switch statements.

```Railroad
Sequence(
	'variant',
	NonTerminal('Identifier'),
    Optional(NonTerminal('GenericParameters')),
	'{',
	ZeroOrMore(Sequence(
		NonTerminal('Identifier'),
		Optional(Sequence('(', Optional(NonTerminal('Type')), ZeroOrMore(Sequence(',', NonTerminal('Type'))), ')')),
		';'
	)),
	'}'
)
```

## Declaring class, interface and enum members

Classes, interfaces, structs and enums can define declaration members, which can be one of the following:

```Railroad
Sequence(
	ZeroOrMore(NonTerminal('Annotation')),
	ZeroOrMore(Choice(0,
		'internal',
		'public',
		'private',
		'mut',
		'take',
		'abstract',
		'final',
		'static',
		'protected',
		'implicit',
		'extern',
		'override'
	)),
	Choice(0,
		NonTerminal('FieldDefinition'),
		NonTerminal('ConstructorDefinition'),
		NonTerminal('MethodDefinition'),
		NonTerminal('SetterDefinition'),
		NonTerminal('GetterDefinition'),
		NonTerminal('ImplementationDefinition'),
		NonTerminal('CallerDefinition'),
		NonTerminal('IndexerDefinition'),
		NonTerminal('OperatorDefinition'),
		NonTerminal('CasterDefinition'),
		NonTerminal('ContainsDefinition'),
		NonTerminal('IteratorDefinition'),
		NonTerminal('Declaration')
	)
)
```

### Field definitions

Classes and strucs can have field members. Fields can be either final (`val`) or nonfinal (`var`) and may have a default value:

```Railroad
Sequence(
	Choice(0, 'val', 'var'),
	NonTerminal('Identifier'),
	Optional(Sequence(':', NonTerminal('Type'))),
	Optional(Sequence('=', NonTerminal('Expression'))),
	';'
)
```

All fields are private by default, making them only accessible by methods of the given class or struct. Fields can only be modified if they are of the nonfinal (`var`) variant. Fields may optionally have an initializer - if the type of the field can be deduced from the initializer, the type of the field may be omitted.

Fields can be declared with a different access level as well:

```
public var myField: int;
```

Although the field itself will remain private, a getter with the specified access level will be generated. If the field is mutable (`var`), a setter will be generated as well. If later on, custom logic is needed on the getter or setter of the field, the public keyword can be omitted and a custom getter and setter generated instead.

### Constructor definitions

Classes can define any number of constructors:

```Railroad
Sequence(
	'this',
	NonTerminal('FunctionHeader'),
	NonTerminal('FunctionBody')
)
```

If a class has no constructor, an empty no-argument constructor will be provided by default.

Upon constructor, all fields must be initialized, and it is a compile-time error for a constructor to complete without initializing every field. Additionally, it is illegal for a constructor to set a final (`val`) field twice. Fields initialization follows the rules below:

- `val` fields with an initializer are already initialized upon object construction. Constructors cannot change their value.
- `var` fields with an initializer are already initialized upon object constructor, but may still be updated by the constructor. (or any other method)
- `val` fields without initializer **must** be initialized exactly once by the constructor.
- `var` fields without initializer, but with a type that has a defined default value, initialization is optional. If the field is not initialized, the default value will be stored.
- `var` fields without initializer and without default value **must** be initializer by the constructor.

Additionally, constructors must not call methods on an object that is not fully initialized. They are also not allow to pass `this` to any method - no code must ever be able observe an object that is not fully initialized:

```
class Point {
	val x: double;
	val y: double;
	
	this(x: double, y: double) {
		this.x = x;
		println("Length: " + length()); // error: attempting to call a method on an incomplete object
		this.y = y;
		// from here on, all fields are initialized, and this is a valid object to use
	}
	
	length() {
		return Math.sqrt(x * x + y * y);
	}
}
```

A derived class is required to call one of the superclass constructors before initializing any fields or using `this`. It does so using the `super` keyword. If no superclass constructor is called explicitly, the empty superclass constructor will be called. If there is no empty superclass constructor, a compile-time error is generated.

### Method definitions

Classes and interfaces may define methods. Methods are defined using their name and a method header, which may consist of zero or more parameter definitions and a return type:

```
class Point {
	...
	
	translate(x: double, y: double): Point {
		...
	}
}
```

If the return type can be deduced from the method body, the return type can be omitted:

```
class Point {
	...
	
	translate(x: double, y: double) {
		return new Point(this.x + x, this.y + y);
	}
	
	scale(scale: double) => new Point(x * scale, y * scale);
}
```

Classes can define virtual methods, which can overridden:

```
class Animal {
	virtual shout() {
		println("?");
	}
}

class Dog {
	override shout() {
		println("Woof!");
	}
}
```

Methods not explicitly defined virtual cannot be overridden. Virtual methods should be used sparingly - instead, if you can, use interfaces instead, in which case all methods are virtual unless they are explicitly declared final.

If a method overrides or implements an existing method, the argument types can be omitted, since they can be inferred from the parent class or interface:

```
interface Shape {
	translate(x: double, y: double);
}

class Circle {
	val x: double;
	val y: double;
	val radius: double;
	
	this(x: double, y: double, radius: double) {
		this.x = x;
		this.y = y;
		this.radius = radius;
	}
	
	implements Shape {
		// argument types can be omitted
		translate(x, y) => new Circle(this.x + x, this.y + y, radius);
	}
}
```

### Getters and setters

### Interface implementations

### Caller definitions

### Indexers

### Caster definitions

### Operator overloading

### Iterator definitions

### Inner types

## Method and function bodies

Methods and functions can be written in one of the following forms:

```Railroad
Choice(1,
	BlockStatement,
	Sequence('=>', NonTerminal('Expression'), ';'),
	';'
)
```

The standard method body is a block statement, which starts with `{` and ends with `}` and may contain any number of statements.

If the return value of a method is a simple expression, a simplified method body can be used instead using the lambda syntax:

```
function length(x: number, y: number) => Math.sqrt(x * x + y * y);
```

Some methods, such as interface method definitions or abstract methods, have no method body at all. In this case a semicolon is used instead.

## Statements

Statements from the

```Railroad
Sequence(
	ZeroOrMore(NonTerminal('Annotation')),
	Choice(0,
		Sequence(NonTerminal('Expression'), ';'),
		NonTerminal('BlockStatement'),
		NonTerminal('ReturnStatement'),
		NonTerminal('VarStatement'),
		NonTerminal('IfStatement'),
		NonTerminal('ForStatement'),
		NonTerminal('DoWhileStatement'),
		NonTerminal('WhileStatement'),
		NonTerminal('ThrowStatement'),
		NonTerminal('TryStatement'),
		NonTerminal('ContinueStatement'),
		NonTerminal('BreakStatement'),
		NonTerminal('SwitchStatement')
	)
)
```

### Block statements

At any point where a statement is expected, a block statement can be used to group multiple statements:

```Railroad
Sequence('{', ZeroOrMore(NonTerminal('Statement')), '}')
```

### Return statements

Return expressions terminate execute of the current function or method and may optionally return a value:

```Railroad
Sequence('return', Optional(NonTerminal('Expression')), ';')
```

If a method is specified to return a value (that is, its return type is not `void`), then a return value **must** be specified. If the method does not return a value (its return type is `void`), it is not permitted to specify a return value.

### Variable declarations

Variable declarations declare a single value and may optionally assign a default value to it. A variable may either be final (`val`) meaning that it cannot be modified after being assigned, or it can be nonfinal (`var`) meaning that it may be modified after initial assignment.

```Railroad
Sequence(
	Choice(1, 'var', 'val'),
	NonTerminal('Identifier'),
	Optional(Sequence(':', NonTerminal('Type'))),
	Optional(Sequence('=', NonTerminal('Expression'))),
	';'
)
```

It is not required to initialize a `val` immediately, but there must be exactly one assignment:

```
val a: string;
a = "hello"; // OK

val b: string;
if condition {
	b = "x";
} else {
	b = "y";
}
println(b); // OK

val c: string;
if condition {
	c = "x";
}
c = "y"; // error: final variable may already be assigned a value
```

Variables must always have their type defined unambiguously. If the type could not be inferred, an error is generated.

```
val a = "hello"; // ok, type is string
val b = 0; // ok, type is int
val c = null; // error, type not clear here
var d = []; // error, what type of array are we declaring here?
```

If the variable type cannot be inferred, a type must be specified explicitly. If the variable is not immediately assigned a value, a type must be defined explicitly.

It is recommended to use `val` as much as possible. Most variables are only assigned once, and using `val` in those case makes it clear that the intent if the assignment is that this is the one and only assignment of this variable, and it will be clear to whoever is reading the code - most of the time, you and yourself - not to look any further for modifications of this variable.

On the other hand, a consistent use of `val` and `var` will also mean that if a variable is declared as a `var`, it is going to be modified somewhere - quite important when reading code.

As an added benefit, it also prevents you from accidentally modifying a variable you didn't intend to.

### For loops

In ZenCode, all for loops are foreach loops, and use the following syntax:

```Railroad
Sequence(
	'for',
	NonTerminal('Identifier'),
	ZeroOrMore(Sequence(',', NonTerminal('Identifier'))),
	'in',
	NonTerminal('Expression'),
	NonTerminal('Statement')
)
```

For loops may loop over values or over keys and values in a list or dictionary:

```
val items = ["a", "b", "c"];
for item in items {
	println(item);
}
for index, item in items {
	println(index + ": " + item);
}

val dict = {a: "x", b: "y", c: "z"};
for key, value in dict {
	println(key + ": " + value);
}
```

If you need to loop over a range of integers, it is possible to do so by looping over a range:

```
for i in 0..10 {
	println(i); // prints 0,1,2,3,4,5,6,7,8,9
}
```

If you need any other kind of loop, it will need to be written as a do/while or while loop instead.

It is not possible to assign to loop variables, that is, they are equivalent to `val` declarations.

### Do-while and while loops

For more flexible looping structures, traditional while and do/while loops are available.

```Railroad
Sequence(
	'while',
	Optional(Sequence(':', NonTerminal('Identifier'))),
	NonTerminal('Expression'),
	NonTerminal('Statement')
)
```

```Railroad
Sequence(
	'do',
	Optional(Sequence(':', NonTerminal('Identifier'))),
	NonTerminal('Statement'),
	'while',
	NonTerminal('Expression'),
	';'
)	
```

While loops will repeat for as long as the given condition is valid, and will immediately stop if the condition resolves to false:

```
var i = 0;
while i < 10 {
	println("Iteration: " + i);
	i++;
}
```

Do-while loops, instead, will always run at least once, and will repeat for as long as the given condition resolves to true:

```
var i = 0;
do {
	println("Iteration: " + i);
} while i < 10;
```

When using nested loops, loops can be named as well, making it possible to break or continue on an outer loop:

```
while:outer conditionA {
	while conditionB {
		if something
			continue outer;
	}
}

do:outer {
	while conditionB {
		if something
			break outer;
	}
} while conditionA
```

### Throw statements

Throw statements can be used to raise an exception, which can later be caught with a try/catch statement:

```Railroad
Sequence('throw', NonTerminal('Identifier'), ';')
```

```
throw new NeverGoingToHappenException();
```

### Switch statements

Switch statements may branch to a number of options depending on an integer, string or enum value:

```Railroad
Sequence(
	'switch',
	NonTerminal('Identifier'),
	'{',
	ZeroOrMore(Choice(1,
		Sequence('case', NonTerminal('Expression'), ':'),
		Sequence('default', ':'),
		NonTerminal('Statement')
	)),
	'}'
)
```

```
var option = 3;
switch option % 2 {
	case 0:
		println("even number");
		break;
	case 1:
		println("odd number");
		break;
}
```

It is illegal for a non-empty case to fall through to a next case, unless the last statement is `continue`:

```
var option = 4;
switch option {
	case 1: // OK, empty cases may fall through
	case 2:
	case 3:
	case 5:
	case 7:
		println("Prime number");
		// error, case must not fall through
	case 10:
		println("You entered ten");
		continue; // OK, can fall through
	case 4:
	case 6:
	case 8:
	case 9:
		println("Not a prime");
		break;
	default:
		println("Number too large");
		// break in the last case is not necessary
}
```

### Break and continue statements

Continue statements can be used to skip execution of a loop:

```Railroad
Sequence('continue', Optional(NonTerminal('Identifier')), ';')
```

Likewise, break statements can be used to break out of a loop altogether:

```Railroad
Sequence('break', Optional(NonTerminal('Identifier')), ';')
```

Break and continue statement will be default skip or break the innermost loop or switch statement. If an outer loop or switch of a nested loop must be targeted instead, an identifier can be given which may denote a different loop. In the case of while or do/while loops, a label can be given; and in the case of a for loop, the name of the looping variable can be used instead. If multiple loop variables are present, any of the loop variable names can be used to target the loop:

```
var total = 0;
for a in [1, 2, 3] {
	for b in [4, 5, 6] {
		total += a * b;
		if total > 10:
			break a; // break out of the outer loop
	}
}
```

## Expressions

### Assignment operators

### Ternary operator

### Combinatorial expressions (&& and ||)

Combinatorial expressions can be used to either:

- Evaluate the right-hand side of an expression if and only if the left-hand side resolves to true or non-null (&&)
- Evaluate the right-hand side of an expression if and only if the left-hand side resolves to false or null (||)

These expressions can be used to combine two conditions, to guard the right-hand side against a certain condition, or as a performance improvement preventing a possible costly expression to be resolved. It can also be used for null handling logic:

```
val x = 5;
if x >= 0 && x < 10 // combine two conditions
	println("x is within range");
if x < 0 || x >= 10
	println("x is out of range");

function foo(dictionary: int[string]) {
	val a = dictionary.get('something'); // type of a is int?
	val b = dictionary.get('something') || 0; // use 0 as default value here
	val c = a && a + 1; // guard against a being null; if a is null, this expression resolves to null
}
```

### Logical and, or and xor

### Comparison expressions

### Contains (in)

### Shift left and shift right

### Addition, subtraction and concatenation

### Multiplication, division and modulo

### Unary operands: negation, inversion and bitwise inversion

### Try expressions

### Accessing members (fields and methods)

### Null-safe operator ?.



### Indexing

### Calling

### Casting

### Increment and decrement

### Lambda expressions

### Range expressions

### Integer constants

### Floating-point constants

### String constants

### $

### This and super

### Arrays

### Dictionaries

### Brackets

### Null, true, false

### New expressions

### Throw expressions

### Panic expressions

### Match expressions

### Bracket expressions

### Type inference in expressions

In many cases, the type of an expression can be inferred from its context. This can be used to resolve ambiguity in many cases and provides some additional benefits as well:

```
function a(items: byte[]) {
	... do something with items ...
}

val x = []; // error: could not infer array type
a([]); // works fine - we know that it's a byte array now
a([1, 2]); // also OK - the array will be a byte array now
var y = [1, 2]; // assumed to be an int array
a(y); // error, cannot cast an int array to an int array

val x: byte[] = []; // type of the expression inferred from the variable type
```

Expression types can be inferred from many sources:

- If the expression is used as function argument, and the type of the parameter is unambiguously known (that is, method overloading didn't result in multiple possible argument types), the type of the expression will be inferred from the argument type.
- If the expression is assigned to a variable, and the type of the variable is already known (for instance, because the variable is explicitly type, or an assignment is being performed to an existing variable), the type of the expression will be inferred to be the variable type
- If the expression is the content of a `switch` or `match` expression, the type of the variable is inferred to be the type of the `switch` or `match` variable.
- If the expression is the left-hand side of an `as` expression, the type of the left-hand side will be inferred to be of the specified cast.
- If the expression is the right-hand side of an `in` expression, the type of the right-hand side will be inferred to be an array of the same type as the left-hand side.
- If the expression is the right-hand side of an equality expression, the type of the right-hand side will be inferred to be of the same type as the left-hand side.

Also, if the type is inferred to be an enum type, it is possible to specify the name of the enum constant directly without qualifying it. Thus the following is possible:

```
enum Animal {
	Cat,
	Dog,
	Tiger
}

val animal = Animal.Cat;
if animal in [Cat, Dog] // equivalent to [Animal.Cat, Animal.Dog]
	println("You can pet this");
if animal === Tiger
	println("Petting is not recommended");
	
println(match animal {
	Cat => "meow",
	Dog => "woof",
	Tiger = "MEOW"
})
```

## Generics

