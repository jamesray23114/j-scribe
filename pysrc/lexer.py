from io import TextIOWrapper

from pysrc.tools import *

# == LEXER DEFINES == 
LEX_INT     = iota(True)
LEX_FLT     = iota()
LEX_CHAR    = iota()
LEX_STR     = iota()
LEX_NAME    = iota()
LEX_OPER    = iota()
LEX_KEYWORD = iota()

STYPES = [
    "int",
    "float",
    "char",
    "string",
    "value",
    "operator",
    "keyword"
]

# == KEYWORD DEFINES ==
KEYWORD_IF      = iota(True)
KEYWORD_ELSE    = iota()
KEYWORD_WHILE   = iota()
KEYWORD_BEGIN   = iota()
KEYWORD_END     = iota()
KEYWORD_FUNC    = iota()
KEYWORD_ENTRY   = iota()

KEYWORD_RPAREN  = iota()
KEYWORD_LPAREN  = iota()
KEYWORD_SEPER   = iota()

    # INTRINSIC TYPES

KEYWORD_VOID    = iota()
KEYWORD_ANY     = iota()    
KEYWORD_INT8    = iota()
KEYWORD_INT16   = iota()
KEYWORD_INT32   = iota()
KEYWORD_INT64   = iota()
KEYWORD_INT     = iota()
KEYWORD_CHAR    = iota()
KEYWORD_PTR     = iota()

SKEYWORDS = [
    "if",
    "else",
    "while",
    "begin",
    "end",
    "func",
    "entry",
    
    "(",
    ")",
    ",",
    
    "void",
    "any"
    "int8",
    "int16",
    "int32",
    "int64",
    "char",
    "ptr"
]

# == OPERATOR DEFINES == 
OPERATOR_ADD    = iota(True)
OPERATOR_SUB    = iota()
OPERATOR_MUL    = iota()
OPERATOR_DIV    = iota()
OPERATOR_MOD    = iota()
OPERATOR_DEBUG  = iota()
OPERATOR_LINDEX = iota()
OPERATOR_RINDEX = iota()

SOPERATORS = [
    "+",
    "-",
    "*",
    "/",
    "%",
    "?",
    "[",
    "]"
]

# == END OF DEFINES ==
class lexer_token:
    
    def __init__(self, location: loc, type: int, data: any) -> None:
        self.location = location
        self.type = type
        self.data = data
        pass
        
    def __repr__(self) -> str:
        if self.type == LEX_KEYWORD:
            return f"{self.location}:".ljust(7) + f"{STYPES[self.type]}(\'{SKEYWORDS[self.data]}\')"
        elif self.type == LEX_OPER:
            return f"{self.location}:".ljust(7) + f"{STYPES[self.type]}(\'{SOPERATORS[self.data]}\')"
        elif self.type == LEX_STR or self.type == LEX_CHAR:
            return f"{self.location}:".ljust(7) + f"{STYPES[self.type]}({self.data})"
        else:
            return f"{self.location}:".ljust(7) + f"{STYPES[self.type]}(\'{self.data}\')"
        
    pass

def ktd(token: str):
    i = 0
    for test in SKEYWORDS:
        if test == token:
            return i
        i += 1
        

def otd(token: str):
    i = 0
    for test in SOPERATORS:
        if test == token:
            return i
        i += 1

def print_lex_token_array(tokens: list[lexer_token]):
    for token in tokens:
        print(" -> [LEXER]: ", end="")
        print(token)

def lex64(file: TextIOWrapper, verbose: bool) -> list[lexer_token]:
    lines = file.readlines()
    
    toklist: list[tuple(str, int, int)] = [] 
    
    for i in range(len(lines)):
        line = lines[i].split("//")[0]
        
        size = len(line)
        while len(line):
            line = line.lstrip()
            comp = ""
            apen = ""
            
            # needed to ensure strings dont get split ie "hello world" doesnt become ("hello), (world")
            if line.startswith("\""): 
                ind = line[1:].find("\"") 
                if ind == -1:
                    error(f"lexor expected a string but got {line} instead")
                comp = line[:ind + 2]
                toklist.append((comp, i + 1, size - len(line) + 1)) 
                line = line [ind + 2:]
                
            else: 
                # removes semicolons
                comp = line.split(" ")[0].rstrip() 
                while comp.endswith(";"):
                    comp = comp[:-1]
                    
                # seperate specific characters from start of token
                if comp.startswith(("(", "[", ",")):
                    toklist.append((comp[0], i + 1, size - len(line) + 1))
                    comp = comp[1:]
                    
                # seperate specific characters from end of token
                if comp.endswith((")", "]", ",")):
                    apen = comp[-1]
                    comp = comp[:-1]
                    
                toklist.append((comp, i + 1, size - len(line) + 1)) 
                toklist.append((apen, i + 1, size - len(line) + 1))
                if " " in line:
                    line = line.split(" ", 1)[1]
                else:
                    break
    
    retlist: list[lexer_token] = []
    
    for token in toklist:
        
        if len(token[0]) == 0:
            continue
        
        if token[0].isnumeric():
            retlist.append(lexer_token(loc(token[1], token[2]), LEX_INT, int(token[0]))) 
            continue
        
        flt = token[0].replace('.', '', 1)
        if flt.isnumeric():
            retlist.append(lexer_token(loc(token[1], token[2]), LEX_FLT, float(token[0])))
            continue
        
        if token[0].startswith("\'") and token[0].endswith("\'"):
            if len(token[0]) != 3:
                error(f"lexor expected a size 1 char but got {token[0]} instead")
            retlist.append(lexer_token(loc(token[1], token[2]), LEX_CHAR, token[0]))
            continue
            
        if token[0].startswith("\"") and token[0].endswith("\""):
            retlist.append(lexer_token(loc(token[1], token[2]), LEX_STR, token[0]))
            continue
        
        if token[0] in SKEYWORDS:
            retlist.append(lexer_token(loc(token[1], token[2]), LEX_KEYWORD, ktd(token[0])))
            continue
        
        if token[0] in SOPERATORS:
            retlist.append(lexer_token(loc(token[1], token[2]), LEX_OPER, otd(token[0])))
            continue
        
        retlist.append(lexer_token(loc(token[1], token[2]), LEX_NAME, token[0]))
        
    if verbose:
        print_lex_token_array(retlist)
        
    return retlist
    
    