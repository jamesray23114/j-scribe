this guide assumes you have a basic understanding of programming, and as such will not go into detail into what each statement here does.

note that this is a work in progress, and as such this guide may not be up to date with the current state of the language. it may have incorrect information, or it may be missing information.

in many situations, information that is missing will follow the format used by the c programming language, assuming it has been implemented.

# hello world 

```
main = {
    print("Hello World")
}
```

# variables

- 7 main types of variables: int, float, string, char, bool, ptr, func
- variables are declared with the syntax: `type name;`

- ptr and func are special types of variables

- ptr types are pointers to other variables, and are declared with the syntax: `ptr<type> name;` 

- func types are pointers to functions, and are declared with the syntax: `func<type -> type> name;` 
- returns are on the right side of the `->` and parameters are on the left.
- note func types can accpet multiple arguments, and return multiple values, both are seperated by commas. i.e. `func<int, int -> int, int> name;`

- variables can be assigned with the syntax: `name = value;`, this can be done all in one line with the syntax: `type name = value;`

- variables can be accessed with the syntax: `name;`, for example: `print(name);`

# functions

- functions are declared with the syntax: `[parameters] { body }`
- functions are assigned to variables with the syntax: `func<type -> type> name = [parameters] { body };`

- function parameters must match the type of the variable they are assigned to, declaring a function with more parameters then it's type can accept will result in an error.
- the opposite however is not true, declaring a function with less parameters then it's type can accept will not result in an error, and will simply ignore the extra parameters. 

- functions can be called with the syntax: `variablename(parameters);`
- this means functions cannot be called if not assigned to a variable, and cannot be called if the variable is not a func type.

- functions can be declared with no parameters, and can be called with no parameters as such: `{ body };`

- note functions can be passed 'annonymously' to other functions as such: `f( [] { body } );`, assumming f is a function that takes a function as a parameter.

# if statements

- if statements work exactly like c, and are declared with the syntax: `if (condition) { body }`
- else if statements work exactly like c, and are declared with the syntax: `else if (condition) { body }`
- else statements work exactly like c, and are declared with the syntax: `else { body }`

- for all of the above, the body can be a single statement, or a block of statements, single statements do not require curly braces, and blocks of statements do.

# while loops

- while loops work exactly like c, and are declared with the syntax: `while (condition) { body }`

- the body can be a single statement, or a block of statements, single statements do not require curly braces, and blocks of statements do.

# for loops

- todo

