from pysrc.tools import *
from pysrc.lexer import *

precedence = {
    "?":    15,
    "++":   1,
    "--":   1,
    "!":    4,
    "$":    4,
    "*":    5,
    "/":    5,
    "%":    5,
    "+":    6,
    "-":    6,
    "<<":   7,
    ">>":   7,
    "&":    8,
    "|":    8,
    "^":    8,
    ">":    8,
    "<":    8,
    ">=":   8,
    "<=":   8,
    "||":   8,
    "&&":   8,
    "!=":   9, 
    "==":   9,
    "=":    10,
    "+=":   10,
    "-=":   10,
    "*=":   10,
    "/=":   10,
    "%=":   10,
    "&=":   10, 
    "|=":   10,
    "^=":   10,
    "<<=":  10,
    ">>=":  10,
}

class expr_token:
    def __init__(self, op: str, x, y) -> None:
        self.op = op
        self.x = x
        self.y = y
        pass
    
    def __repr__(self) -> str:
        return f"({self.op}, {self.x}, {self.y})"
    
    def ins(self, mod):
        if precedence[self.op] > precedence[mod.op]:
            if type(self.y) != expr_token:
                mod.x = self.y
                self.y = mod
                mod = self
                return mod
            else:
                temp = self.y.ins(mod)
                return expr_token(self.op, self.x, temp)
            
        elif precedence[self.op] <= precedence[mod.op]:
            mod.x = self
            return mod


    
class compiler_token:
    def __init__(self, location: loc, type: int, data: any) -> None:
        self.location = location
        self.type = type
        self.data = data
        pass
    
    def __repr__(self) -> str:
        return f"{context.STRING[self.type]} {self.data}"            

class context:
    EXPR    = iota(True)
    STRLIT  = iota()
    INTLIT  = iota()
    FLTLIT  = iota()
    INST    = iota()
    
    STRING = [
        "expression",
        "string literal",
        "int literal",
        "float literal",
        "instruction"
    ]
    
    def __init__(self) -> None:
        self.retlist    = []
        self.typelist   = ["int", "int8", "int16", "int32", "int64", "void", "char", "float"]
        self.varlist    = []
        self.funclist   = []
        self.lstack     = []
        
    def __repr__(self) -> str:
        s = ""
        s += f"retlist:                \n" 
        s += f"    {self.retlist}      \n"
        s += f"typelist:               \n" 
        s += f"    {self.typelist}     \n"
        s += f"varlist:                \n" 
        s += f"    {self.varlist}      \n"
        s += f"funclist:               \n"
        s += f"    {self.funclist}     \n"
        s += f"lstack:                 \n"
        s += f"    {self.lstack}       \n"
        return s
        
    def pushtype(self, data: str):
        self.typelist.append(data)
        
    def pushret(self, location, type, data):
        self.retlist.append(context.compiler_token(location, type, data))

    def pushvar(self, data: any):
        self.varlist.append(data)

    def pushfunc(self, data: any):
        self.funclist.append(data)

    def pushlstack(self, data: ltok):
        self.lstack.append(data)
        
    def poplstack(self) -> ltok:
        if len(self.lstack) == 0:
            return None
        else:
            return self.lstack.pop()
        
    def peeklstack(self) -> ltok:
        if len(self.lstack) == 0:
            return None
        else:
            return self.lstack[-1]
        
        

def process(tokarr: list[ltok], verbose: bool) -> context:
    
    ret = context()
    currentfile = ""
    
    i = 0
    while i < len(tokarr):
        token = tokarr[i]
        
        match (token.type):
            case (LEX.INT):
                ret.pushlstack(token)    
            case (LEX.FLT):
                ret.pushlstack(token)
            case (LEX.CHAR):
                ret.pushlstack(token)
            case (LEX.STR):
                ret.pushlstack(token)
            case (LEX.NAME):
                ret.pushlstack(token)
                
            case (LEX.UNARY):
                match token.data:
                    case "?":
                        ret.pushlstack(token)
                    case _:
                        ptodo(f"impliment unary operator {token.data}")
            
            case (LEX.BINARY):
                tokprev = ret.peeklstack()
                i += 1
                toknext = tokarr[i]
                
                if tokprev is None:
                    error(f"{token.location}: binary operator {token.data} expects a leading value but got nothing instead")
                if toknext.type == LEX.FILE:
                    error(f"{token.location}: binary operator {token.data} expects a preceding value but got nothing instead")
                
                tokprev = ret.poplstack()
                if type(tokprev) == ltok:
                    if tokprev.type == LEX.INT:
                        ret.pushlstack(ltok(tokprev.location, LEX.EXPR, expr_token(token.data, tokprev.data, toknext.data)))
                    elif tokprev.type == LEX.STR:
                        ret.pushlstack(ltok(tokprev.location, LEX.EXPR, expr_token(token.data, tokprev.data, toknext.data)))
                    elif tokprev.type == LEX.FLT:
                        ret.pushlstack(ltok(tokprev.location, LEX.EXPR, expr_token(token.data, tokprev.data, toknext.data)))
                    elif tokprev.type == LEX.NAME:
                        ret.pushlstack(ltok(tokprev.location, LEX.EXPR, expr_token(token.data, tokprev.data, toknext.data)))
                    elif tokprev.type == LEX.EXPR:
                        tokprev.data = tokprev.data.ins(expr_token(token.data, None, toknext.data))
                        ret.pushlstack(tokprev)
                    else:
                        error(f"binary operator {token.data} expects a numeric value but got {token} instead // ptodo")
                        
                else:
                    error(f"{token.location}: compiler ran into unexpected token {tokprev}")
                        
            case (LEX.KEY):
                ptodo("case LEX.KEYWORD")
            case (LEX.FILE):
                if token.data == "EOF":
                    currentfile = ""
                else:
                    currentfile = token.data
            
            case (_):
                error(f"compiler ran into unexpected token {token.data}")
                
        i += 1
        pass # while i < len(tokarr)
    
    if verbose:
        print(ret)  
    
    return ret

def compile64_to_oparray(tokarr: list[ltok], verbose: bool) -> list[compiler_token]:
    
    dat = process(tokarr, verbose)
    
    ptodo("compiler stage 2")
    
    