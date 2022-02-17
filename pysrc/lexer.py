from io import TextIOWrapper

from pysrc.tools import *

# == LEXER DEFINES == 
class LEX:
    INT     = iota(True)
    FLT     = iota()
    CHAR    = iota()
    STR     = iota()
    NAME    = iota()
    OPER    = iota()
    KEYWORD = iota()
    FILE    = iota()

    STRING = [
        "int",
        "float",
        "char",
        "string",
        "value",
        "operator",
        "keyword",
        "file"
    ]

class KEYWORD:
    IF      = iota(True)
    ELSE    = iota()
    WHILE   = iota()
    BEGIN   = iota()
    END     = iota()
    FUNC    = iota()
    RETURN  = iota()
    ENTRY   = iota()

    # INTRINSIC TYPES

    VOID    = iota()
    ANY     = iota()    
    INT8    = iota()
    INT16   = iota()
    INT32   = iota()
    INT64   = iota()
    INT     = iota()
    CHAR    = iota()
    FLOAT   = iota()
    PTR     = iota()

    STRING = [
        "if",
        "else",
        "while",
        "begin",
        "end",
        "func",
        "return",
        "entry",

        "void",
        "any",
        "int8",
        "int16",
        "int32",
        "int64",
        "int",
        "char",
        "float",
        "ptr"
    ]

# == OPERATOR DEFINES == 
class OPERATOR:
    ADD    = iota(True)
    SUB    = iota()
    MUL    = iota()
    DIV    = iota()
    MOD    = iota()
    DEBUG  = iota()
    LINDEX = iota()
    RINDEX = iota()
    GR     = iota()
    LS     = iota()

    STRING = [
        "+",
        "-",
        "*",
        "/",
        "%",
        "?",
        "[",
        "]",
        ">",
        "<",
    ]   

SEPARATORS = [
    ",",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}", 
    "<",
    ">",
    
    ";",
    " ",
    "\n",
    "\t"  
]

# == END OF DEFINES ==
class lexer_token:
    
    def __init__(self, filename: str, location: loc, type: int, data: any) -> None:
        self.filename = filename
        self.location = location
        self.type = type
        self.data = data
        pass
        
    def __repr__(self) -> str:        
        if self.type == LEX.KEYWORD:
            return f"| {self.filename}:{self.location}:".ljust(35) + f"| {LEX.STRING[self.type]}(\'{KEYWORD.STRING[self.data]}\')".ljust(60) + "|"
        elif self.type == LEX.OPER:
            return f"| {self.filename}:{self.location}:".ljust(35) + f"| {LEX.STRING[self.type]}(\'{OPERATOR.STRING[self.data]}\')".ljust(60) + "|"
        elif self.type == LEX.STR or self.type == LEX.CHAR:
            return f"| {self.filename}:{self.location}:".ljust(35) + f"| {LEX.STRING[self.type]}({self.data})".ljust(60) + "|"
        else:
            return f"| {self.filename}:{self.location}:".ljust(35) + f"| {LEX.STRING[self.type]}(\'{self.data}\')".ljust(60) + "|"
        
    pass

def ktd(token: str):
    i = 0
    for test in KEYWORD.STRING:
        if test == token:
            return i
        i += 1
        

def otd(token: str):
    i = 0
    for test in OPERATOR.STRING:
        if test == token:
            return i
        i += 1

def print_lt_token_array(tokens: list[lexer_token]):
    print("  [LEXR]: ", end="")
    print("| filename: ".ljust(35) + "| type:".ljust(60) + "|")
    print("  [LEXR]: | =================================|===========================================================|")
    for token in tokens:
        print("  [LEXR]: ", end="")
        print(token)
    print("  [LEXR]: | =================================|===========================================================|")



def lex64(file: TextIOWrapper, verbose: bool) -> list[lexer_token]:
    data = file.read() + "\n"
    
    toklist: list[tuple(str, int, int)] = [] 
    
    apn = ""
    x = 1
    y = 1
    
    instring = False
    incomment = False
    
    for char in data:
        
        if char == ";" and not instring:
            incomment = True
        
        elif char == "\n" and incomment:
            y += 1
            incomment = False
          
        elif incomment:
            continue
        
        elif char == "\"":
            apn += char
            x += 1
            if instring:
                toklist.append((apn, x - len(apn), y))
                apn = ""
                instring = False
            else:
                instring = True
                
        elif char == "\n" and instring == True:
            error(f"lexer expected a string at {file.name}:{y}:{x - len(apn)} but got {apn} instead")
        
        elif char in SEPARATORS and instring == False:
            if len(apn) != 0:
                toklist.append((apn, x - len(apn), y))
                apn = ""
            x += 1
            
            if char == "\n":
                y += 1
                x = 1
            elif not char.isspace():
                toklist.append((char, x - 1, y))
            else:
                pass
        else:
            apn += char
            x += 1
    
    toklist.append((apn, x, y))
    
    retlist: list[lexer_token] = []
    retlist.append(lexer_token(file.name, loc(0, 0), LEX.FILE, file.name))
    
    for token in toklist:
        
        if len(token[0]) == 0:
            continue
        
        if token[0].isnumeric():
            retlist.append(lexer_token(file.name, loc(token[2], token[1]), LEX.INT, int(token[0]))) 
            continue
        
        flt = token[0].replace('.', '', 1)
        if flt.isnumeric():
            retlist.append(lexer_token(file.name, loc(token[2], token[1]), LEX.FLT, float(token[0])))
            continue
        
        if token[0].startswith("\'") and token[0].endswith("\'"):
            if len(token[0]) != 3:
                error(f"lexor expected a size 1 char but got {token[0]} instead")
            retlist.append(lexer_token(file.name, loc(token[2], token[1]), LEX.CHAR, token[0]))
            continue
            
        if token[0].startswith("\"") and token[0].endswith("\""):
            retlist.append(lexer_token(file.name, loc(token[2], token[1]), LEX.STR, token[0]))
            continue
        
        if token[0] in KEYWORD.STRING:
            retlist.append(lexer_token(file.name, loc(token[2], token[1]), LEX.KEYWORD, ktd(token[0])))
            continue
        
        if token[0] in OPERATOR.STRING:
            retlist.append(lexer_token(file.name, loc(token[2], token[1]), LEX.OPER, otd(token[0])))
            continue
        
        retlist.append(lexer_token(file.name, loc(token[2], token[1]), LEX.NAME, token[0]))
        
    retlist.append(lexer_token(file.name, loc(retlist[-1].location.x + 1, 0), LEX.FILE, "EOF"))
        
    if verbose:
        print_lt_token_array(retlist)
        
    return retlist
    
    