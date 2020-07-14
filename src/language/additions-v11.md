# ZenCode 1.1 Extensions

## Typed enums

Enums can be declared as typed enums, eg:

```
enum UserRole: int {
    User, // automatically assigned the value 0
    Admin, // automatically assigned the value 1
    Helpdesk(100)
}

enum Color: string {
    Red('red'),
    Green('green'),
    Blue('blue')
}
```

It is possible to convert from this enum to its value type implicitly, or from its value type to enum type explicitly.
Note that it is possible for enum values to hold values that are unspecified, and as such, match expressions must always have a default value.

Typed enums cannot have fields or constructors, but they may have (static or non-static) member methods.
