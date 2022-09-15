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
    FILE        = auto()
    
    UNIT        = auto()
    PROGRAM     = auto()
    
    EXPR        = auto()
    VALUE       = auto()
    
    COMPARE     = auto()
    LOGIC       = auto()
    SHIFT       = auto()
    FACTOR      = auto()
    SUM         = auto()
    
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
        return self.type == other.type # data and location are ignored
        
    def __repr__(self) -> str:
        if self.data is None:
            return f"{self.loc}:" + allign(self.loc, 27) + f"{self.type} \n"
        if type(self.data) is list:
            strlist = str(self.data)
            strlist = strlist.replace(", ", "\t")
            strlist = strlist.replace("[", "\t")
            strlist = strlist.replace("]", "")
            return f"{self.loc}:" + allign(self.loc, 27) + f"{self.type}" + allign(self.type, 10) + "\n" + f"{strlist}"
        else:
            return f"{self.loc}:" + allign(self.loc, 27) + f"{self.type}" + allign(self.type, 12) + f" {self.data} \n"
    
def allign(text: any, width: int) -> str:
    return " " * (width - (len(str(text))))
    
def error(msg: str):
    print("[\u001b[31;1m", end="")
    print("ERROR", end="")
    print("\u001b[0m]: ", end="")
    print(msg)
    print("[INFO]: exiting...")
    exit(0)
    
def todo(func: str, msg: str):
    print("[\u001b[33;1m", end="")
    print("TODO", end="")
    print("\u001b[0m]: ", end="")
    print(f"implement \'{msg}\' at {func}")
    print("[INFO]: exiting...")
    exit(0)
    
def warn(msg: str):
    print("[\u001b[33;1m", end="")
    print("WARN", end="")
    print("\u001b[0m]: ", end="")
    print(msg)
    
def info(msg: str):
    print("[INFO]: ", end="")
    print(msg)
    
def printTokArray(tokens: list[token], prefix: str = ""):
    for token in tokens:
        print(prefix + str(token), end="")
     
def usage():
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