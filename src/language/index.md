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

Preprocessor instructions are treated as whitespace, but target environments may choose to process them. It is up to the target environment to choose how these are processed, the ZenCode language itself does not assign any meaning to these comments. Preprocessor comments starting with a double hash (## something) and an exclamation mark (#! something) are reserved for future ZenCode processing. Additionally, if a file starts with a comment #! it will be guaranteed to be ignored in any future versions of ZenCode (thus can be safely used to indicate the program to execute the script).

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

Identifiers starting with $ are treated especially, and $ itself is a special identifier as well. $ identifiers are called "local identifiers" and have a meaning depending on their context. In a class, $ identifiers always refer to a field. This makes it possible to assign to a field instead of a setter, or as a short form to set fields:

```
class MyClass {
	test: int { public get };
	
	this(test: int) {
		$test = test; // doesn't invoke the setter
	}
	
	set test: int {
		if $ >= 0
			$test = $;
	}
}
```

The "$" identifier itself has two possible meanings:

- In a setter, $ specifies the value that is currently being set. (as used in the example above)
- When indexing an array, $ is set to the length of the array. This makes it easy to access the last (or nth last) element in an array: `myArray[$ - 1]`

Note that both may be nested, in which case the inner definition dominates.


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
final
finally
float
for
function
get
if
in
immutable
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
        NonTerminal('StructDeclaration'),
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

## Declaring class, interface, struct and enum members

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
	Optional(Sequence('{',
		Optional(Sequence(
			Optional(Choice(0, 'public', 'internal', 'protected', 'private')),
			Choice(0, 'get', 'set'),
			Optional(Sequence(
				',',
				Optional(Choice(0, 'public', 'internal', 'protected', 'private')),
				Choice(0, 'get', 'set')
			))
		))
	)),
	Optional(Sequence('=', NonTerminal('Expression'))),
	';'
)
```

All fields are private and can only be accessed by methods of the given class or struct.

However, there is a shorthand syntax to automatically generate the getters and setters:

```
var myField: int { get, set };
```

These getters and setters are public by default, but can be mode protected or internal as well:

```
var myField: int { protected get }
```

Fields can only be modified if they are of the nonfinal (`var`) variant and the method that modifies them is marked `mut`. For any method not marked mut, the current object is essentially immutable.

For instance, the following would be fine:

```
class MyClass {
	var field: int = 0;
	
	mut increment() {
		this.field++;
	}
}
```

But the following examples won't compile:

```
class MyFaultyClassA {
	val field: int = 0;
	
	mut increment() {
		this.field++; // error: field is final
	}
}

class MyFaultyClassB {
	var field: int = 0;
	
	increment() {
		this.field++; // error: increment is not mut
	}
}
```

### Constructor definitions

Classes can define any number of constructors:

```Railroad
Sequence(
	'this',
	NonTerminal('FunctionHeader'),
	NonTerminal('FunctionBody')
)
```



### Method definitions

### Getter definitions

### Setter definitions

### Implementation definitions

### Caller definitions

### Indexer definitions

### Caster definitions

### Operator definitions

### Iterator definitions

### Inner types
