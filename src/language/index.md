# ZenCode Language Specification

## Introduction

The ZenCode programming language is a general programming language focused on the capability of being translated to various systems. This allows code to be written once and then used on a wide variety of platforms, including web (javascript), mobile (Android / iOS) and servers. It is a high-level language and is focused on getting the job done efficiently. Although performance is considered important, clarity of coding has a higher priority: it is indended to be a practical language, easy to read and write, and easy to understand.

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

The following whitespace token types exist:

- Scripting instructions: ```#[^\n]*[\n\\e]```
- Single-line comment: ```//[^\n]*```
- Multi-line comment: ```/\\*([^\\*]|(\\*+([^\\*/])))*\\*+/```
- Whitespace: ```( |\t|\r|\n)```

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

Inside strings, escape sequences may be used. The following escape sequences exist in both single-quoted and double-quoted strings:

- ```\b``` (backspace)
- ```\f``` (line feed)
- ```\n``` (newline)
- ```\r``` (carriage return)
- ```\t``` (tab)
- ```\&{named-character};``` for a named character

Named characters such as ```\&copy;``` or ```\&reg;``` are supported and make it easy to read and write commonly used special characters. The full list of named characters can be found [here](namedcharacters.html).

Strings and identifiers may be prefered by the @ character. An identifier prefixed by @ is indentical by the identifier without the prefix, however, keywords may be used. Thus a variable that should be named "final" can then be named "@final" to prevent it from being interpreted as the final keyword.

A string literal prefixed by the @ character is interpreted as wysiwyg string. In such string, escape characters are not processed, but the ' or " character cannot occur.

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

![Railroad](Diagram(ZeroOrMore(Sequence('import', OneOrMore(NonTerminal('Identifier')))), ZeroOrMore(Choice(0, NonTerminal('Declaration'), NonTerminal('Statement')))))

A declaration can be a class, interface, struct, enum, variant or function . Although it is recommended to have a single declaration per file and to give the file the exact same name as its declaration, it is not required to do so.

## Addendum 1: Scripting instructions 

