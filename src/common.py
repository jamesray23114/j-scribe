from enum import Enum, auto

class LEXER(Enum):
    INT     = auto()
    FLOAT   = auto()
    CHAR    = auto()
    STRING  = auto()
    ID      = auto()
    
    HASH    = auto()
    OP      = auto()   
    GROUP   = auto()
    
    COMMA   = auto()
    SEMI    = auto()
    FILE    = auto()
    EOF     = auto()

    SPACE   = auto()
    
class PARSER(Enum):
    FILE        = auto()
    
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
    def __init__(self, loc: location, type: Enum, data: any) -> None:
        self.loc = loc
        self.type = type
        self.data = data
        
    def __eq__(self, other) -> bool:
        if other is token:
            return self.type == other.type # data and location are ignored
        else:
            return self.type == other
        
    def __repr__(self) -> str:
        if self.data is None:
            return f"{self.loc}:" + allign(self.loc, 27) + f"{self.type} \n"
        else:
            return f"{self.loc}:" + allign(self.loc, 27) + f"{self.type}" + allign(self.type, 12) + f" {self.data} \n"
    
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
    
def printTokArray(tokens: list[token], prefix: str = "") -> str:
    """ returns a string representation of a list of tokens
    
    NEARING DEPRECATION: waiting for replacement method   

    Args:
        tokens (list[token]): list of tokens to print
        prefix (str, optional): prefix to print before each token. Defaults to "".


    Returns:
        str: string representation of the list of tokens
    """
    out = ""
    for token in tokens:
        out += prefix + str(token)
    return out
        
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