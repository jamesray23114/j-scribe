# j-scribe

j-scribe is a wip programming language that compiles to native machine code.

the main goal is to make a language with the same amount of power as C, but with a more robust allaround toolkit.

## example compiler usage as of now
python bec.py -v -c examples/current.jbe

## planned 'unique' features

- functions as types
    - functions are stored as variables and act like pointers
    - functions can be passed as arguments to other functions, and can even be passed 'anonymously' 
    - functions can be returned from other functions
    - functions can return multiple values

- built in macros and metaprogramming
    - there can exist compile time functions that can be used to generate code (like iota() in go)
    - macros will be type safe (if it makes sense in that scenario) and the compiler will inform you if you use a macro in a way that is not type safe

- built in assembler and the ability to interact with in in normal code
    - the registers will be kept track of by the compiler, so you can't accidentally overwrite a register
    - the compiler will also attempt to keep track of the stack, and can inform you if you risk overwriting the stack

- compiler hints
    - the compiler will ideally be able to infer a lot of things, but you can also give it hints to help it along
    - you can tell the compiler that a function will never return, so it can optimize the code accordingly
    - you can tell the compiler the likelyhood of a branch being taken, so it can optimize the code accordingly
    - ect.

- built in package manager
    - not really a unique feature, but it's something that I want to have

