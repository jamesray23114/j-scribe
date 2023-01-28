from src.common import *
from src.analysis import *
    
            
def compile64(ast: token, symb: tuple[list[function], list[variable]], verbose: bool):
    
    glt = reserve(symb)
    il = makeil(ast, glt)
    
    #todo: check if main exists before adding call to main
    
    for tok in il:
        print(tok)
           
    return il
    
def getsize(t: str) -> int:
    if t == "int":
        return 4
    if t == "float":
        return 4
    if t == "string":
        return 8
    if t == "char":
        return 1
    if t == "bool":
        return 1
    if t == "void":
        return 0
    if t == "ptr":
        return 8
    if t == "func":
        return 8
    
def reserve(symb: tuple[list[function], list[variable]]):
    glt = []
    
    for var in symb[1]:
        glt.append((var.name, getsize(var.type.typename)))
        
    return glt
    
def makeil(ast: token, glt: list[tuple[str, int]]):
    out = []
    
    if isinstance(ast, program):
        pass
    
    elif isinstance(ast, unit):
        for tok in ast.value:
            out += makeil(tok, glt)
    
    elif isinstance(ast, vardecl):
        pass
    
    elif isinstance(ast, varassign):
        
        if isinstance(ast.value, funcdecl):
            out += makeil(ast.value, glt)
            
        
    elif isinstance(ast, funcdecl):
        
        for tok in ast.body:    
            out += makeil(tok, glt)
               
    elif isinstance(ast, funccall):
        for tok in ast.args:
            out.append(il_push(ast.loc, tok))
                
        out.append(il_call(ast.loc, ast.name.value))

    elif isinstance(ast, returnstate):
        out.append(il_push(ast.loc, ast.value))
        out.append(il_return(ast.loc))
             
    else:
        todo(f"makeil", f"{type(ast).__name__}")
             
    return out

    
    
    

    
