from io import TextIOWrapper

from pysrc.tools import *

# == LEXER DEFINES == 
class LEX:
    INT     = iota(True)
    FLT     = iota()
    CHAR    = iota()
    STR     = iota()
    NAME    = iota()
    UNARY   = iota()
    BINARY  = iota()
    KEY     = iota()
    FILE    = iota()
    EXPR    = iota()

    STRING = [
        "int",
        "float",
        "char",
        "string",
        "value",
        "unary",
        "binary",
        "keyword",
        "file",
        "expression"
    ]

class KEY:
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
class UNARY:
    STRING = [
        "++",
        "--",
        "!",
        "?",
        "$"
    ]

class BINARY:
    STRING = [
        "+",
        "-",
        "*",
        "/",
        "%",
        "&",
        "|",
        "^",
        "<<",
        ">>",
        
        "=",
        "+=",
        "-=",
        "*=",
        "/=",
        "%=",
        "&=",
        "|=",
        "^=",
        "<<=",
        ">>=",
        
        "!=",
        "==",
        ">",
        "<",
        ">="
        "<=",
        "||",
        "&&"
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
    "=",
    
    ";",
    " ",
    "\n",
    "\t"  
]
    
# == END OF DEFINES ==
class ltok:
    
    def __init__(self, location: loc, type: int, data: any) -> None:
        self.location = location
        self.type = type
        self.data = data
        pass
        
    def __repr__(self) -> str:        
        return f"{LEX.STRING[self.type]}(\'{self.data}\')"   
    pass

def print_lt_token_array(tokens: list[ltok]):
    print("  [LEXR]: ", end="")
    print("| filename: ".ljust(35) + "| type:".ljust(60) + "|")
    print("  [LEXR]: | =================================|===========================================================|")
    for token in tokens:
        print("  [LEXR]: ", end="")
        print(f"| {token.location}:".ljust(35) + f"| {LEX.STRING[token.type]}({token.data})".ljust(60) + "|")
    print("  [LEXR]: | =================================|===========================================================|")


def lex64(file: TextIOWrapper, verbose: bool) -> list[ltok]:
    data = file.read() + "\n"
    toklist: list(tuple(str, int, int)) = []
    
    apn = ""
    x = 1
    y = 1
    instring = False
    incomment = False
    
    # parse file into list seperated by SEPERATORS
    
    for char in data:
        if char == ";" and not instring:
            incomment = True
        
        elif char == "\n" and incomment:
            incomment = False
            y += 1
            
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
    
    # translate strings to tokens
           
    retlist: list[ltok] = [ltok(loc(file.name,  0, 0), LEX.FILE, file.name)]
    
    for token in toklist:
        if len(token[0]) == 0:
            continue
        
        elif token[0].isnumeric():
            retlist.append(ltok(loc(file.name, token[2], token[1]), LEX.INT, int(token[0]))) 
            
        
        elif token[0].replace('.', '', 1).isnumeric():
            retlist.append(ltok(loc(file.name, token[2], token[1]), LEX.FLT, float(token[0])))
            
        elif token[0].startswith("\'") and token[0].endswith("\'"):
            if len(token[0]) != 3:
                error(f"lexor expected a size 1 char but got {token[0]} instead")
            retlist.append(ltok(loc(file.name, token[2], token[1]), LEX.CHAR, token[0]))
        
        elif token[0].startswith("\"") and token[0].endswith("\""):
            retlist.append(ltok(loc(file.name, token[2], token[1]), LEX.STR, token[0]))
        
        elif token[0] in KEY.STRING: 
            retlist.append(ltok(loc(file.name, token[2], token[1]), LEX.KEY, token[0]))
            
        elif token[0] in UNARY.STRING: 
            retlist.append(ltok(loc(file.name, token[2], token[1]), LEX.UNARY, token[0]))
            
        elif token[0] in BINARY.STRING: 
            retlist.append(ltok(loc(file.name, token[2], token[1]), LEX.BINARY, token[0]))
            
        else:
            retlist.append(ltok(loc(file.name, token[2], token[1]), LEX.NAME, token[0]))
            
    retlist.append(ltok(loc(file.name, retlist[-1].location.x + 1, 0), LEX.FILE, "EOF"))
    
    if verbose:
        print_lt_token_array(retlist)
    
    return retlist
    
    