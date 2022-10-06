from enum import Enum, auto

class LEXER(Enum):
    INT     = auto()
    FLOAT   = auto()
    CHAR    = auto()
    STRING  = auto()
    ID      = auto()
    
    OP      = auto()   
    GROUP   = auto()
    
    COMMA   = auto()
    SEMI    = auto()
    FILE    = auto()
    EOF     = auto()

    SPACE   = auto()
    
class PARSER(Enum):
    UNIT        = auto()
    PROGRAM     = auto()
    
    EXPR        = auto()
    CONDITION   = auto()
    LOGIC       = auto()
    SUMMAND     = auto()
    FACTOR      = auto()
    UNARY       = auto()
    VALUE       = auto()
    
    PREPROC     = auto()
    
    VARDECL     = auto()
    FUNCDECL    = auto()
    CLASSDECL   = auto()
    VARASSIGN   = auto()
    FUNCCALL    = auto()
    
    IF          = auto()
    WHILE       = auto()
    FOR         = auto()
    RETURN      = auto()
    
    TYPE        = auto()
    
    INDEX       = auto()
    MEMBER      = auto()
    BOOL        = auto()
    
class ANALYSIS(Enum):
    
    FUNCTION    = auto()
    VARIABLE    = auto()
    
class location:
    def __init__(self, file: str, x: int, y: int) -> None:
        self.file = file
        self.x = x
        self.y = y
        
    def __repr__(self) -> str:
        return f"{self.file}:{self.x}:{self.y}"

class token:
    def __init__(self, loc: location) -> None:
        self.loc = loc
        
class lexer:
    pass
    
class scribe:
    pass

class parser:
    pass

class analysis:
    pass

class compiler:
    pass

class interpreter:
    pass

class runtime:
    pass
                  
# lexer token types:

class int(token):
    def __init__(self, loc: location, data: int) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        return f"int: {self.value}"
    
class float(token):
    def __init__(self, loc: location, data: float) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        return f"float: {self.value}"
        
class char(token):
    def __init__(self, loc: location, data: str) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        return f"char: {self.value}"
        
class string(token):
    def __init__(self, loc: location, data: str) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        return f"string: {self.value}"
        
class id(token):
    def __init__(self, loc: location, data: str) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        return f"ident: {self.value}"

class op(token):
    def __init__(self, loc: location, data: str) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        return f"operator: {self.value}"
    
class group(token):
    def __init__(self, loc: location, data: str) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        return f"group: {self.value}"
    
class comma(token):
    def __init__(self, loc: location) -> None:
        super().__init__(loc)
        
    def __str__(self) -> str:
        return f"comma"
    
class semi(token):
    def __init__(self, loc: location) -> None:
        super().__init__(loc)
        
    def __str__(self) -> str:
        return f"semi"
    
class file(token):
    def __init__(self, loc: location) -> None:
        super().__init__(loc)
        
    def __str__(self) -> str:
        return f"file: {self.loc.file}"

class eof(token):
    def __init__(self, loc: location) -> None:
        super().__init__(loc)
        
    def __str__(self) -> str:
        return f"eof: {self.loc.file}"
    
# parser token types:
class unit(token):
    def __init__(self, loc: location, data: list[token]) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        out = "unit: {\n"
        out += f"\t location: {self.loc}"
        out += "\t data: {\n"
        out += "\t\t" + "\n\t\t".join([str(x) for x in self.value])
        out += "\t }\n" 
        
        return out
    
class program(token):
    def __init__(self, loc: location, data: list[unit]) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        out = "program: {\n"
        out += f"\t location: {self.loc}"
        out += "\t data: {\n"
        out += "\t\t" + "\n\t\t".join([str(x) for x in self.value])
        out += "\t }\n" 
        
        return out
    
class expr(token):
    def __init__(self, loc: location, ) -> None:
        super().__init__(loc)
        self.value = data
        
        return out
    
def allign(text: any, width: int) -> str:
    """ returns a string with 'width' spaces after 'text'

    Args:
        text (any): text to allign, will be converted to string
        width (int): width of the alligned text

    Returns:
        str: alligned text
    """
    return " " * (width - (len(str(text))))
    
def error(msg: str):
    """ prints an error message and exits

    Args:
        msg (str): message to print
    """
    print("[\u001b[31;1m", end="")
    print("ERROR", end="")
    print("\u001b[0m]: ", end="")
    print(msg)
    print("[INFO]: exiting...")
    exit(0)
    
def todo(func: str, msg: str):
    """ prints a todo message and exits

    Args:
        func (str): function to work on
        msg (str):  message to print
    """
    print("[\u001b[33;1m", end="")
    print("TODO", end="")
    print("\u001b[0m]: ", end="")
    print(f"implement \'{msg}\' at {func}")
    print("[INFO]: exiting...")
    exit(0)
    
def warn(msg: str):
    """ prints a warning message

    Args:
        msg (str): message to print
    """
    print("[\u001b[33;1m", end="")
    print("WARN", end="")
    print("\u001b[0m]: ", end="")
    print(msg)
    
def info(msg: str):
    """ prints an info message

    Args:
        msg (str): message to print
    """
    print("[INFO]: ", end="")
    print(msg)
         
def usage():
    """ prints the usage of the program and exits
    """
    
    print("Usage: scribe [options] file")
    print("options:")
    print("\t -c                    compile file")
    print("\t -r                    run file after compiling")
    print("\t -i                    run and remove file after compiling")
    print("\t -o outfile            output redirection (default=$file)")
    print("\t -vl,--verbose_lex     verbose lexer output")
    print("\t -vx,--verbose_com     verbose compiler output")
    print("\t -h,--help             prints this screen")
    print("\t -S outfile            Write asm to file and keep asm")
    exit(0)