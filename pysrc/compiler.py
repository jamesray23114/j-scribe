from distutils.debug import DEBUG
from numpy import mat
from pysrc.tools import *
from pysrc.lexer import *

class CTX:
    DEBUG = iota(True)
    
    STRING = [
        "debug"
    ]

class compiler_token:
    
    def __init__(self, name: str, location: loc, context: int, data: any) -> None:
        self.name = name
        self.location = location
        self.context = context
        self.data = data
        pass
    
    def __repr__(self) -> str:
        return f"| {self.name}:{self.location}:".ljust(25) + f"| {self.data}".ljust(60) + "|"
    
    pass

class ctx_debug:
    def __init__(self, type: int, data: any) -> None:
        self.type = type
        self.data = data
        pass

    def __repr__(self) -> str:
        return f"operator debug(type: {LEX.STRING[self.type]},".ljust(30) + f"data: {self.data})"

    pass

def print_ct_token_array(tokarr: list[compiler_token]):
    print("  [COMP]: ", end="")
    print("| filename:".ljust(25) + "| type:".ljust(60) + "|")
    print("  [COMP]: | =======================|===========================================================|")
    for token in tokarr:
        print("  [COMP]: ", end="")
        print(token)
    print("  [COMP]: | =======================|===========================================================|")

def compile64_to_oparray(tokarr: list[lexer_token], verbose: bool) -> list[compiler_token]:
    
    currentfile = ""
    currenttoken = ""
    retlist: list[compiler_token] = []
    
    i = 0
    try: 
        while i < len(tokarr):
            match tokarr[i].type:
                
                case LEX.FILE:
                    if tokarr[i].data == "EOF":
                        currentfile = ""
                    else:
                        currentfile = tokarr[i].data
                
                case LEX.INT:
                    error(f"compiler expected an expression but got int {tokarr[i].data} instead")
                
                case LEX.STRING:
                    error(f"compiler expected an expression but got string {tokarr[i].data} instead")
                
                case LEX.FLT:
                    error(f"compiler expected an expression but got float {tokarr[i].data} instead")
                    
                case LEX.CHAR:
                    error(f"compiler expected an expression but got char {tokarr[i].data} instead")
                    
                case LEX.OPER:
                    match tokarr[i].data:
                        case OPERATOR.DEBUG:
                            i += 1
                            retlist.append(
                                compiler_token(currentfile, tokarr[i-1].location, CTX.DEBUG, 
                                    ctx_debug(tokarr[i].type, tokarr[i].data)
                                )
                            )
                        
                        
                        
                        case _:
                            ptodo(f"operator \'{OPERATOR.STRING[tokarr[i].data]}\'")
                    
                case LEX.NAME:
                    ptodo("compiler names")
                    
                case LEX.KEYWORD:
                    ptodo("compiler keywords")
                
                case _:
                    error(f"compiler got unexpected token {tokarr[i]}")
        
            i += 1
        
        
    except IndexError:
        error(f"compiler expected a token and got nothing instead.")
        
    if verbose:
        print_ct_token_array(retlist)
        
    return retlist