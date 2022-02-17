from pysrc.tools import *
from pysrc.lexer import *

class CTX:
    DEBUG   = iota(True)
    ADD     = iota()
    SUB     = iota()
    MUL     = iota()
    DIV     = iota()
    MOD     = iota()
    LOAD    = iota()
    NONE    = iota() 
    
    STRING = [
        "dump",
        "add",
        "sub",
        "mul",
        "div",
        "mod",
        "load",
        "none"
    ]

# compiler_token

class compiler_token:
    
    def __init__(self, name: str, location: loc, context: int, data: any) -> None:
        self.name = name
        self.location = location
        self.context = context
        self.data = data
        pass
    
    def __repr__(self) -> str:
        return f"| {self.name}:{self.location}:".ljust(35) + f"| {CTX.STRING[self.context]}({self.data})".ljust(60) + "|"
    
# CTX_DEBUG

class CTX_DEBUG:
    STR     = iota(True)
    INT     = iota()
    FLT     = iota()
    
    STRING = [
        "string",
        "int",
        "float",
    ]
        
    def __init__(self, type: int, value: any) -> None:
        self.type = type
        self.value = value

    def __repr__(self) -> str:
        if self.type == CTX_DEBUG.INT:
            dat = "["
            for tok in self.value:
                dat += f"{CTX.STRING[tok.context]}({tok.data}), "
            return dat[0:-2] + "]"
        else:
            return f"data: {self.value}"

def print_ct_token_array(tokarr: list[compiler_token]):
    print("  [COMP]: ", end="")
    print("| filename:".ljust(35) + "| type:".ljust(60) + "|")
    print("  [COMP]: | =================================|===========================================================|")
    for token in tokarr:
        print("  [COMP]: ", end="")
        print(token)
    print("  [COMP]: | =================================|===========================================================|")

def compile64_to_oparray(tokarr: list[lexer_token], verbose: bool) -> list[compiler_token]:
    
    currentfile = ""
    retlist: list[compiler_token] = []
    ltstack: list[lexer_token] = []
    dtypes = ["int", "int8", "int16", "int32", "int64", "void", "char", "float"]
    
    i = 0
   
    while i < len(tokarr):
        match tokarr[i].type:
            
            case LEX.FILE:
                if tokarr[i].data == "EOF":
                    currentfile = ""
                else:
                    currentfile = tokarr[i].data
            
            case LEX.INT | LEX.FLT | LEX.STR | LEX.CHAR:
                ltstack.append(tokarr[i])
                
            case LEX.OPER:
                match tokarr[i].data:
                    case OPERATOR.DEBUG:
                        last = tokarr[i]
                        i += 1
                        
                        match tokarr[i].type:
                            case LEX.NAME:
                                ptodo("debug name")
                            
                            case LEX.STR | LEX.CHAR:
                                curr = tokarr[i]
                                retlist.append(compiler_token(curr.filename, curr.location, CTX.DEBUG, CTX_DEBUG(CTX_DEBUG.STR, curr.data)))
                            case LEX.INT | LEX.FLT:
                                curr = tokarr[i]
                                expr = [curr]
                                i += 1
                                
                                while tokarr[i].type in [LEX.INT, LEX.OPER, LEX.FLT]:
                                    if tokarr[i].type == LEX.OPER and tokarr[i].data not in [OPERATOR.ADD, OPERATOR.SUB, OPERATOR.MUL, OPERATOR.DIV, OPERATOR.MOD]:
                                        i -= 1
                                        break
                                    expr.append(tokarr[i])
                                    i += 1
                                
                                if len(expr) == 1:
                                    retlist.append(compiler_token(curr.filename, curr.location, CTX.DEBUG, CTX_DEBUG(CTX_DEBUG.STR, f"\"{curr.data}\"")))
                                else:
                                    expr.append(tokarr[-1])
                                    expr = compile64_to_oparray(expr, False)
                                    retlist.append(compiler_token(curr.filename, curr.location, CTX.DEBUG, CTX_DEBUG(CTX_DEBUG.INT, expr)))
                                
                            case LEX.FILE:
                                error(f"{last.filename}:{last.location}: operator \'?\' expects 1 argument but got nothing instead")
                                
                            case _:
                                error(f"{last.filename}:{last.location}: operator \'?\' expects 1 printable argument but got \'{last.data}\' instead")
                    
                    case OPERATOR.ADD | OPERATOR.SUB | OPERATOR.MUL | OPERATOR.DIV | OPERATOR.MOD:
                        curr = tokarr[i]
                        i += 1
                        if len(ltstack) == 0 or tokarr[i].type == LEX.FILE:
                            error(f"{curr.filename}:{curr.location}: operator \'{OPERATOR.STRING[curr.data]} expected 1 argument but got nothing instead\'")
                        lhs = ltstack.pop()
                        rhs = tokarr[i]
                        ltstack.append(lexer_token(curr.filename, curr.location, LEX.INT, 0))
                        
                        if lhs.type == LEX.INT:
                            if lhs.data == 0:
                                pass
                            else:
                                retlist.append(compiler_token(curr.filename, curr.location, CTX.LOAD, lhs.data))
                        elif lhs.type == LEX.FLT:
                            ptodo("float math")
                        else:
                            error(f"{curr.filename}:{curr.location}: operator \'{OPERATOR.STRING[curr.data]} expected 1 argument but got \'{lhs.data}\' instead\'")
                        
                        if curr.data == OPERATOR.ADD and rhs.type == LEX.INT:
                            if rhs.data == 0:
                                pass
                            else:
                                retlist.append(compiler_token(curr.filename, curr.location, CTX.ADD, rhs.data))
                        elif curr.data == OPERATOR.ADD and rhs.type == LEX.FLT:
                            ptodo("float math")
                        elif curr.data == OPERATOR.SUB and rhs.type == LEX.INT:
                            if rhs.data == 0:
                                pass
                            else:
                                retlist.append(compiler_token(curr.filename, curr.location, CTX.SUB, rhs.data))
                        elif curr.data == OPERATOR.SUB and rhs.type == LEX.FLT:
                            ptodo("float math")
                        elif curr.data == OPERATOR.MUL and rhs.type == LEX.INT:
                            retlist.append(compiler_token(curr.filename, curr.location, CTX.MUL, rhs.data))
                        elif curr.data == OPERATOR.MUL and rhs.type == LEX.FLT:
                            ptodo("float math")
                        elif curr.data == OPERATOR.DIV and rhs.type == LEX.INT:
                            retlist.append(compiler_token(curr.filename, curr.location, CTX.DIV, rhs.data))
                        elif curr.data == OPERATOR.DUV and rhs.type == LEX.FLT:
                            ptodo("float math")
                        elif curr.data == OPERATOR.MOD and rhs.type == LEX.INT:
                            retlist.append(compiler_token(curr.filename, curr.location, CTX.MOD, rhs.data))
                        elif curr.data == OPERATOR.MOD and rhs.type == LEX.FLT:
                            ptodo("float math")
                        else:
                            error(f"{curr.filename}:{curr.location}: operator \'{OPERATOR.STRING[curr.data]} expected 1 argument but got \'{rhs.data}\' instead\'")
                                                    
                    case _:
                        ptodo(f"compiler operator \'{OPERATOR.STRING[tokarr[i].data]}\'")
            
            case LEX.NAME:
                ptodo("compile named values")
            
            case LEX.KEYWORD:
                ptodo("compile keywords")
            
            case _:
                error(f"compiler got unexpected token {tokarr[i]}")
        
        i += 1
                
    if verbose:
        print_ct_token_array(retlist)
        
    return retlist