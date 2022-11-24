# ZenCode system architecture

## Runtime architecture

The ZenCode runtime architecture is modeled as follows:

- A given host application may contain one or more scripting engines
- A scripting engine usually contains multiple modules, each of which contain a piece of functionality
- Modules may contain definitions and scripted code

[images/runtime_model.png]

### Host applications

ZenCode scripts will always run in the context of a given application, which determines which functions and libraries will be available to the scripts running in it.

It's the host application which will:

- Create scripting engines
- Register available modules to the scripting engines (including standard libraries and host APIs)
- Tell the scripting engine to start execution
- Cleanup values that "escaped" the scripting engine (usually through host APIs)

### Scripting engines

A scripting engine is used to compile and run scripts. Scripting engines may contain any number of modules. It's up to the host system how to split executable code into modules; it could combine multiple scripts into a single module, or it may use a module for each script, or a mix of both. Multiple modules may contain executable code.

Modules usually have dependencies. Usually a scripting engine will contain one or more standard libraries, one or more modules to provide a so-called "Host API" containing functions and classes that can be used to communicate with the host application, as well as other libraries that a host system decided to load (perhaps on behalf of a script that indicated to need it).

If a host application contains multiple scripting engines, they always run independently of each other. They cannot interact, except perhaps if the host API provides functionality to do so.

### Modules

Modules may contain a script and one or more definitions. Definitions may be functions or class/interface/enum/variant definitions.

Multiple modules may contain scripts, but their order of execution is implementation-dependent.

## Development tools and debugging

