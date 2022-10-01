from src.common import *
from src.lexer  import *
from src.parse  import *

def analyze64(ast: token, verbose: bool):
    
    makeID.val = 0
    symb = make_symboltable(ast)
    
    # main
    symb[1].append(makeglobalvar("main", makeglobaltype(
        "func",
        [
            makeglobaltype("int"),                                  # argc  
            makeglobaltype("ptr", [ makeglobaltype("string") ]),    # argv
            makeglobaltype("ptr", [ makeglobaltype("string") ])     # envp
        ],
        [ makeglobaltype("int") ]                                   # exit code
    )))                                
    
    # print
    symb[1].append(makeglobalvar("print", makeglobaltype(
        "func",
        [ makeglobaltype("string") ],                               # string
    )))
    
    # __syscall int, int, int, int, int, int, int
    symb[1].append(makeglobalvar("__syscall", makeglobaltype(
        "func",
        [ 
            makeglobaltype("int"),                                # rax
            makeglobaltype("int"),                                # rdi
            makeglobaltype("int"),                                # rsi
            makeglobaltype("int"),                                # rdx
            makeglobaltype("int"),                                # r10
            makeglobaltype("int"),                                # r8
            makeglobaltype("int")                                 # r9
        ],
        [ makeglobaltype("int") ]                                 # return
    )))
    
    makeID.val = 0
    verf = verify(ast, symb)
    
    
    todo("analyze64", "analyze")
    
def makeID() -> int:
    makeID.val += 1
    return makeID.val
    
def makeglobaltype(type: str, generics = [], returns = []):
    glb = location("global", 0, 0)
    
    if returns != []:
        return token(glb, PARSER.TYPE, [token(glb, LEXER.ID, [type]), generics, returns])
    elif generics != [] and returns == []:
        return token(glb, PARSER.TYPE, [token(glb, LEXER.ID, [type]), generics])
    else:
        return token(glb, PARSER.TYPE, [token(glb, LEXER.ID, [type])])
    
def makeglobalvar(name: str, type):
    
    glb = location("global", 0, 0)
    
    out = token(glb, ANALYSIS.VARIABLE, [])
    out.data.append([])
    out.data.append(0)
    out.data.append(type)
    out.data.append(token(glb, LEXER.ID, name))
    
    return out
        
def make_symboltable(ast: token, loc: list[int] = []) -> tuple[list[token], list[token]]:
    
    functions = []
    variables = []
    
    if ast.type == PARSER.UNIT:
        for tok in ast.data:
            r = make_symboltable(tok, loc)
            functions += r[0]
            variables += r[1]
            
    elif ast.type == PARSER.PREPROC:
        pass
    
    elif ast.type == PARSER.VARDECL:
        out = token(ast.loc, ANALYSIS.VARIABLE, [])
        temp = loc.copy()
        out.data.append(temp)
        out.data.append(makeID())
        out.data.append(ast.data[0])
        out.data.append(ast.data[1])
        variables.append(out) 
    
    elif ast.type == PARSER.FUNCDECL:
        out = token(ast.loc, ANALYSIS.FUNCTION, [])
        temp = loc.copy()
        temp.append(makeID())
        out.data.append(loc.copy())
        out.data.append(temp[-1])
        out.data.append(ast.data[0])
        functions.append(out)
        for tok in ast.data[1]:
            r = make_symboltable(tok, temp)
            functions += r[0]
            variables += r[1]
    
    elif ast.type == PARSER.VARASSIGN:
        if ast.data[2].type == PARSER.FUNCDECL:
            r = make_symboltable(ast.data[2], loc)
            functions += r[0]
            variables += r[1]
        
    elif ast.type == PARSER.IF:
        temp = loc.copy()
        temp.append(makeID())
        for tok in ast.data[1]:
            r = make_symboltable(tok, temp)
            functions += r[0]
            variables += r[1]
            
        
        if ast.data[2] is not None:
            for ifstate in ast.data[2]:
                temp = loc.copy()
                temp.append(makeID())
                for tok in ifstate.data[1]:
                    r = make_symboltable(tok, temp)
                    functions += r[0]
                    variables += r[1]
            
        if ast.data[3] is not None:
            temp = loc.copy()
            temp.append(makeID())
            for tok in ast.data[3]:
                r = make_symboltable(tok, temp)
                functions += r[0]
                variables += r[1]

    elif ast.type == PARSER.WHILE:
        temp = loc.copy()
        temp.append(makeID())
        for tok in ast.data[1]:
            r = make_symboltable(tok, temp)
            functions += r[0]
            variables += r[1]
    
    return functions, variables



def find_tok(tok: token, symb: tuple[list[token], list[token]], loc: list[int]) -> token:
    """ 
        returns a token from the symbol table whose id matches 'tok' and
        ensures the token has no duplicates + exists in the current scope
        
        Args:
            tok (token):  the id token whose name is searched for
            symb (tuple): the symbol table
            loc (list[int]):  the current scope
        
        Returns:
            token: the token from the symbol table
    """
    out = 0
    main = 0
    
    for var in symb[1]:
        if var.data[3].data == tok.data:
            if not check_scope(var, loc):
                continue
            if var.data[3].data == "main" and main == 0:
                main = var
                out = var
            elif out != 0:
                out = var
            else:
                error(f"{tok.loc}: variable '{tok.data}' has duplicate definitions")
    
    if main != 0:
        out = main
    
    if out == 0:
        error(f"{tok.loc}: variable '{tok.data}' is not defined")
    
    return out

def check_scope(tok: token, loc: list[int]) -> bool:
    """ verifies that the token is in the current scope 

    Args:
        tok (token): the token to check
        loc (list[int]): the current scope

    Returns:
        bool: whether the token is in the current scope
    """
    
    if loc == [] and tok.data[0] != []:
        return False
    
    if tok.data[0] == []:
        return True
    
    for i in range(len(loc)):
        if tok.data[0][i] != loc[i]:
            return False
    
    return True


def check_type(tok: token) -> bool:

    stypes = [ #simple types
        "int",
        "bool",
        "string",
        "char",
        "float",
        "void"
    ]

    ctypes = [ #complex types
        "ptr",
        "func"
    ]

    
    if tok.data[0].data in stypes:
        if len(tok.data) == 1:
            return True
        else:
            error(f"{tok.loc}: type '{tok.data[0].data}' cannot have modifiers")
    
    elif tok.data[0].data in ctypes:
        if len(tok.data) == 2:
            for t in tok.data[1]:
                check_type(t)
            return True
        elif len(tok.data) == 3:
            
            if tok.data[0].data == "ptr":
                error(f"{tok.loc}: pointer type cannot have return types")
            
            for t in tok.data[1]:
                check_type(t)
            for t in tok.data[2]:
                check_type(t)
            return True
        else:
            return True
    error(f"{tok.loc}: invalid type '{tok.data[0].data}'")
 

def verify(ast: token, symb: tuple[list[token], list[token]], loc: list[int] = []) -> token:
    
    #print(symb)
    
    if ast.type == PARSER.UNIT:
        for tok in ast.data:
            ast = verify(tok, symb, loc)
        
    
    elif ast.type == PARSER.PREPROC:
        pass
    
    elif ast.type == PARSER.VARDECL:
        makeID()
        
        check_type(ast.data[0])
        
        todo("verify", "verify vardecl") 
            # [ ] check if vardecl has valid type
            # [ ] check if id is valid
            # [ ] check if id is in scope
            
    elif ast.type == PARSER.FUNCDECL:
        makeID()
        todo("verify", "verify funcdecl") 
            # [ ] check if arglist matches
            
    elif ast.type == PARSER.VARASSIGN:
        
        temp = find_tok(ast.data[0], symb, loc)
        
        todo("verify", "verify varassign")
            # [x] check if id exists
            # [x] check if id is in scope
            # [ ] check if type matches
            
    elif ast.type == PARSER.IF:
        makeID()
        todo("verify", "verify if")
            # [ ] check if expression is bool
            # [ ] check if expression (vars) is in scope
    
    elif ast.type == PARSER.WHILE:
        makeID()
        todo("verify", "verify while")
            # [ ] check if expression is bool
            # [ ] check if expression (vars) is in scope
            
    elif ast.type == PARSER.EXPR:
        todo("verify", "verify expr")
            # [ ] check if expression is valid
            # [ ] check if expression (vars) is in scope
            
    elif ast.type == PARSER.RETURN:
        todo("verify", "verify return")
            # [ ] check if return type matches
            
    elif ast.type == PARSER.TYPE:
        todo("verify", "verify type")
            # [ ] check if type is valid
    
    pass