from src.common import *
from src.lexer  import *
from src.parse  import *

def analyze64(ast: token, verbose: bool):
    """ analyzes the ast assuming 64 bit architecture

    TODO: finish this function

    Args:
        ast (token): the root ast token
        verbose (bool): if true, prints out the symbol table, type information, and other information
    """
    
    
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
    
    if verbose:
        if not os.path.exists(".out"):
            os.mkdir(".out")
            print(" -> [ANYLS]: created .out directory")
            
        if not os.path.exists(".out/analysis"):
            os.mkdir(".out/analysis")
            print(" -> [ANYLS]: created .out/analysis directory")
            
        with open(".out/analysis/" + "symb_" + ast.loc.file.split("/")[-1], "w") as file:
            out = "symbol table: {\n"
            out += "functions: {\n"
            out += "\n".join([str(x) for x in symb[0]])
            out += "\n}\n\n\n"
            out += "variables: {\n"
            out += "\n".join([str(x) for x in symb[1]])
            out += "\n}\n"
            out += "}\n"
            out = indentTree(out)
            file.write(out)
        
        print(" -> [ANYLS]: wrote tokens to .out/analysis/" + "symb_" + ast.loc.file.split("/")[-1])
    
    makeID.val = 0
    verify(ast, symb)
    
    
    return symb

def makeID() -> intl:
    """ makes a unique ID (int) for each variable and function

    Args:
        makeID.val (int): the current ID, should be 0 at the start of each anylysis stage

    Returns:
        int: unique ID
    """
    
    makeID.val += 1
    return makeID.val
    
def makeglobaltype(type: str, generics = [], returns = []) -> token:
    """ makes a global type for use in intrinsic varaibles / functions

    TODO: determine if there is a better way to do this, should be changed when types are changed

    Args:
        type (str): the name of the type being made
        generics (list, optional): list of generic types.
        returns (list, optional): list of return types. 

    Returns:
        token: a valid token of type PARSER.TYPE 
    """
    
    glb = location("global", 0, 0)
    
    if returns != []:
        return typep(glb, type, generics, returns)
    elif generics != [] and returns == []:
        return typep(glb, type, generics)
    else:
        return typep(glb, type)
    
def makeglobalvar(name: str, type: typep) -> variable:
    """ makes a global variable to add to the symbol table

    TODO: determine if there is a better way to do this, should be changed when types are changed

    Args:
        name (str): the name of the variable
        type (typep): the type of the variable

    Returns:
        varaibles: a valid varaible token
    """
    
    glb = location("global", 0, 0)
    out = variable(glb, [], name, type)
    return out
        
def make_symboltable(ast: token, loc: list[intl] = []) -> tuple[list[token], list[token]]:
    """ returns a list of all variables and functions in the program

    TODO: determine a more efficient way to do this
    TODO: determine if varaibles need a unique ID
    TODO: determine if other information needs to be stored in the symbol table
    TODO: classes, enums, unions, etc.
    TODO: provide more information about what is stored in *.data, such as what is stored in each index (unions would help here...)

    Args:
        ast (token): the root ast token
        loc (list[int], optional): the current scope, used by this function

    Returns:
        tuple[list[token], list[token]]:
            [0]: list of all functions in the program 
            [1]: list of all variables in the program
    """
    
    functions = []
    variables = []
    
    if isinstance(ast, unit):
        curr: unit = ast
        for tok in curr.value:
            r = make_symboltable(tok, loc)
            functions += r[0]
            variables += r[1]
    
    elif isinstance(ast, vardecl):
        curr: vardecl = ast
        tloc = loc.copy()
        variables.append(variable(curr.loc, tloc, curr.name, curr.type))
        
        if isinstance(curr.value, funcdecl):
            r = make_symboltable(curr.value, loc)
            functions += r[0]
            variables += r[1]

    
    elif isinstance(ast, funcdecl):
        curr: funcdecl = ast
        
        
        tloc = loc.copy()
        tloc.append(makeID())
        
        functions.append(function(curr.loc, tloc, makeID(), curr.args, curr.defaults))
        
        for tok in curr.body:
            r = make_symboltable(tok, tloc)
            functions += r[0]
            variables += r[1]
              
    elif isinstance(ast, varassign):
        curr: varassign = ast
        
        if isinstance(curr.value, funcdecl):
            r = make_symboltable(curr.value, loc)
            functions += r[0]
            variables += r[1]
        
    elif isinstance(ast, ifstate):
        curr: ifstate = ast
        
        tloc = loc.copy()
        tloc.append(makeID())
        
        
        for tok in curr.body:
            r = make_symboltable(tok, tloc)
            functions += r[0]
            variables += r[1]
        
        if curr.ifelse:
            for tok in curr.ifelse:
                curr2: ifstate = tok
                
                tloc = loc.copy()
                tloc.append(makeID())
                
                for tok in curr2.body:
                    r = make_symboltable(tok, tloc)
                    functions += r[0]
                    variables += r[1]
                    
        if curr.elsebody:
            tloc = loc.copy()
            tloc.append(makeID())
            
            for tok in curr.elsebody:
                r = make_symboltable(tok, tloc)
                functions += r[0]
                variables += r[1]

    elif isinstance(ast, whilestate):
        curr: whilestate = ast
        
        tloc = loc.copy()
        tloc.append(makeID())
        
        for tok in curr.body:
            r = make_symboltable(tok, tloc)
            functions += r[0]
            variables += r[1]
    
    return functions, variables

def find_tok(tok: token, name: str, symb: tuple, scope: list[intl]) -> variable:
    """ returns a token from the symbol table whose id matchs the given token
        ensures the tokens has no duplicates and exists within the current scope

    TODO: this allows for a variables declared later in a scope to be used before it is declared, not this is fine for global variables, but not for local variables
    TODO: keep track of where a varaible is declared and used, this will be used to determine if a varaible is used before it is declared

    Args:
        tok (token): the token to lookup
        symb (tuple): the symbol table
        loc (list[intl], optional): the current scope

    Returns:
        token: the token from the symbol table
        error: halts the program if the token is not found or duplicates are found
    """
    
    out = None
    main = None
    
    
    for var in symb[1]: # variables
        var: variable
        
        if var.name == name: 
            if not check_scope(var, scope): 
                continue
        
            
            if var.name == "main" and main is None: 
                main = var
            elif out == None:
                out = var
            else:
                error(f"{tok.loc}: variable '{name}' has duplicate definitions")
                
    if main != None:
        out = main
    
    if out == None:
        error(f"{tok.loc}: variable '{name}' is not defined")
            
    return out

def check_scope(var: variable, scope: list[intl]) -> bool:
    """ verifies that the token is in the current scope 

    Args:
        tok (token): the token to check
        loc (list[int]): the current scope

    Returns:
        bool: true if token is in the current scope, false otherwise
     """

    if scope == [] and var.scope != []: 
        return False
    
    if var.loc == []:
        return True
    
    if len(scope) > len(var.scope):
        return True
    
    for i in range(len(scope)):
        if scope[i] != var.scope[i]:
            return False
    
    return True

mathop = ["+", "-", "*", "/", "%"]
def check_math(op: str, lhs: str, rhs: str, loc: location) -> str:
    if lhs.split(":")[0] == "id":
        lhs = lhs.split(":")[1]
    if rhs.split(":")[0] == "id":
        rhs = rhs.split(":")[1]
    
    match lhs, rhs:
        case ("int", "int"):
            return "int"
        case ("int", "float"):
            return "float"
        case ("float", "int"):
            return "float"
        case ("float", "float"):
            return "float"
        
    error(f"{loc}: invalid math operation '{op}' between '{lhs}' and '{rhs}'")

logicop = ["==", "!=", ">", "<", ">=", "<="]
def check_logic(op: str, lhs: str, rhs: str, loc: location) -> str:
    if lhs.split(":")[0] == "id":
        lhs = lhs.split(":")[1]
    if rhs.split(":")[0] == "id":
        rhs = rhs.split(":")[1]
    
    match(lhs, rhs):
        case ("int", "int"):
            return "bool"
        case ("int", "float"):
            return "bool"
        case ("float", "int"):
            return "bool"
        case ("float", "float"):
            return "bool"
        
        case ("bool", "bool"):
            if op in ["==", "!="]:
                return "bool"
    error(f"{loc}: invalid logic operation '{op}' between '{lhs}' and '{rhs}'")
    
bitop = ["&", "|", "^", "<<", ">>"]
def check_bitwise(op: str, lhs: str, rhs: str, loc: location) -> str:
    if lhs.split(":")[0] == "id":
        lhs = lhs.split(":")[1]
    if rhs.split(":")[0] == "id":
        rhs = rhs.split(":")[1]
        
    match(lhs, rhs):
        case ("int", "int"):
            return "int"
        
    error(f"{loc}: invalid bitwise operation '{op}' between '{lhs}' and '{rhs}'")

unaryop = ["u+", "u-", "~", "!", "u*", "u&", "l++", "l--", "r++", "r--"]
def check_unary(op: str, tok: str, loc: location) -> str:
     
    if tok == "int":
        if op in ["u&, u*"]:
            error(f"{loc}: cannot use unary operator '{op}' on a int literal")
        return "int"

    elif tok == "float":
        if op in ["u&, u*"]:
            error(f"{loc}: cannot use unary operator '{op}' on a float literal")
            
    elif tok == "string":
        error(f"{loc}: cannot use unary operator '{op}' on a string literal")
    
    elif tok == "char":
        error(f"{loc}: cannot use unary operator '{op}' on a char literal")
    
    elif tok == "bool":
        if op == "!":
            return "bool"
        error(f"{loc}: cannot use unary operator '{op}' on a bool literal")
        
    elif tok.split(":")[0] == "id":
        if op == "u&":
            return "ptr:" + "".join(str(s) for s in tok.split(":")[1:]) # returns ptr:type
        if op == "u*":
            if tok.split(":")[1] == "ptr":
                return "".join(str(s) for s in tok.split(":")[2:]) # returns type from ptr
            else:
                error(f"{loc}: cannot dereference a non pointer")
        return check_unary(op, tok.split(":")[1], loc)
        
    else:
        todo(f"type '{tok}' not implemented for unary operator '{op}'", "check_unary")
    
def get_typename(tok: token, symb, scope) -> str:
    if isinstance(tok, intl):
        return "int"
    if isinstance(tok, floatl):
        return "float"
    if isinstance(tok, stringl):
        return "string"
    if isinstance(tok, charl):
        return "char"
    if isinstance(tok, booll):
        return "bool"
    
    if isinstance(tok, id):
        temp = find_tok(tok, tok.value, symb, scope)
        out = "id:" + temp.type.typename
        if temp.type.generics:
            out += ":" + ":".join(str(s) for s in temp.type.generics)
        return out
    
    if isinstance(tok, index):
        temp = find_tok(tok, tok.name.value, symb, scope)
        
        if isinstance(tok.index, intl):
            return temp.type.generics[0].typename
        if isinstance(tok.index, id):
            if get_typename(tok.index, symb, scope) == "id:int":
                return temp.type.generics[0].typename
        if isinstance(tok.index, expr):
            if check_expr_type(tok.index, symb, scope) == "int":
                return temp.type.generics[0].typename
        error(f"{tok.loc}: array index must be an integer")
        
    error(f"{tok.loc}: cannot get type of token '{type(tok)}'")

def check_expr_type(tok: expr, symb: tuple, scope: list[intl] = []) -> str:
    
    lhs = ""
    rhs = ""
    
    if isinstance(tok.lhs, expr):
        lhs = check_expr_type(tok.lhs, symb, scope)
    else:
        lhs = get_typename(tok.lhs, symb, scope)
    
    if not tok.rhs is None:
        if isinstance(tok.rhs, expr):
            rhs = check_expr_type(tok.rhs, symb, scope)
        else:
            rhs = get_typename(tok.rhs, symb, scope)
        
        
    if tok.op in mathop:
        return check_math(tok.op, lhs, rhs, tok.loc)
    elif tok.op in logicop:
        return check_logic(tok.op, lhs, rhs, tok.loc)
    elif tok.op in bitop:
        return check_bitwise(tok.op, lhs, rhs, tok.loc)
    elif tok.op in unaryop:
        return check_unary(tok.op, lhs, tok.loc)
    else:
        error(f"{tok.loc}: unknown operator '{tok.op}'")
     
def check_type(var: variable, compare: token, symb: tuple, scope: list[intl]):
    """ checks if the compare token contains the correct date to match the given type

    TODO: allow for soft conversions, such as int to float, float to int, etc.
    TODO: allow for type casts

    Args:
        type (variable): the type to check
        compare (token): the token to check
        symb (tuple): the symbol table
        scope (list[intl]): the current scope
        
    Returns:
        error: halts the program if the token does not match the type
    """    
    
    rval = ""
    typename = ""
    if isinstance(var, variable):
        typename = var.type.typename
    else:
        typename = var.typename
    
    if isinstance(compare, expr):
        rval = check_expr_type(compare, symb, scope)
        
    if isinstance(compare, id):
        temp = find_tok(compare, compare.value, symb, scope)
        rval = temp.type.typename
    
    if isinstance(compare, index):
        rval = get_typename(compare, symb, scope)
    
    if typename == "int":
        if isinstance(compare, intl) or rval == "int":
            return 
        if rval:
            error(f"{compare.loc}: expected type 'int', got '{rval}' instead.")
        else:
            error(f"{compare.loc}: expected type 'int', got '{type(compare)}' instead.")

    elif typename == "float":
        if isinstance(compare, floatl) or rval == "float":
            return 
        if rval:
            error(f"{compare.loc}: expected type 'int', got '{rval}' instead.")
        else:
            error(f"{compare.loc}: expected type 'float', got '{type(compare)}' instead.")
            
    elif typename == "char":
        if isinstance(compare, charl) or rval == "char":
            return 
        if rval:
            error(f"{compare.loc}: expected type 'int', got '{rval}' instead.")
        else:
            error(f"{compare.loc}: expected type 'char', got '{type(compare)}' instead.")
            
    elif typename == "string":
        if isinstance(compare, stringl) or rval == "string":
            return 
        if rval:
            error(f"{compare.loc}: expected type 'int', got '{rval}' instead.")
        else:
            error(f"{compare.loc}: expected type 'string', got '{type(compare)}' instead.")
            
    elif typename == "bool":
        if isinstance(compare, booll) or rval == "bool":
            return 
        if rval:
            error(f"{compare.loc}: expected type 'int', got '{rval}' instead.")
        else:
            error(f"{compare.loc}: expected type 'bool', got '{type(compare)}' instead.")
            
    elif typename == "void":
        if compare == None:
            return 
        error(f"{compare.loc}: expected no data, got '{type(compare)}' instead.")

    elif typename == "ptr":
        if rval.split(":")[0] == "ptr":
            for i in range(len(var.type.generics)):
                if var.type.generics[i].typename != rval.split(":")[i+1]:
                    error(f"{compare.loc}: expected type 'ptr:{var.type.generics[i].typename}', got '{rval}' instead.")
            return
        error(f"{compare.loc}: expected pointer, got '{rval}' instead.")
        
        
    elif typename == "func":
        if isinstance(compare, funcdecl):
            compare: funcdecl
            
            tloc = scope.copy()
            tloc.append(makeID())
            
            tsymb = tuple(symb)    
            if var.type.generics is None:
                if compare.args:
                    error(f"{compare.loc}: expected no arguments, got {len(compare.args)} instead.")
            else:
                if len(compare.args) > len(var.type.generics):
                    error(f"{compare.loc}: too many arguments for function '{var.name}'")

                for t, arg in zip(var.type.generics, compare.args):
                    v = variable(compare.loc, tloc, arg, t)
                    tsymb[1].append(v)
                    find_tok(var, arg, tsymb, tloc)
            
            verify.cfunc = var
            verify(compare, tsymb, tloc)
            del verify.cfunc
        
        else:
            error(f"{compare.loc}: expected type 'func', got '{type(compare)}' instead.")
        
        
    else:
        error(f"{var.loc}: unknown type '{typename}'")
        
def check_typename(tok: typep):
    """ checks if the 'type' token has a valid type name

    TODO: custom types

    Args:
        tok (token): the token to check, must be of type PARSER.TYPE

    Returns:
        bool: returns true if the type name is valid
        error: halts program on error
    """


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

    if tok.typename in stypes:
        if tok.generics or tok.returns:
            error(f"{tok.loc}: type '{tok.typename}' cannot have generics") 
        return True
    
    if tok.typename == "ptr":
        if tok.generics:
            if len(tok.generics) > 1:
                error(f"{tok.loc}: pointer type can only have one generic")
            else:
                check_typename(tok.generics[0])
                
        if tok.returns:
            error(f"{tok.loc}: pointer type cannot have a return type")
                
        return True
    
    if tok.typename == "func":
        if tok.generics:
            for i in tok.generics:
                check_typename(i)
            
        if tok.returns:
            if len(tok.returns) > 1:
                error(f"{tok.loc}: function type can only have one return type")
            for i in tok.returns:
                check_typename(i)
            
        return True
 
def verify(ast: token, symb: tuple[list[token], list[token]], loc: list[intl] = []):
    """ verifies the syntax of the program

    TODO: finish this

    Args:
        ast (token): the abstract syntax tree
        symb (tuple): the symbol table
        loc (list[int]): the current scope, used internally. Defaults to [].

    Returns:
        token: ?
    """    
    
    if isinstance(ast, program):
        todo("verify", "program")
    
    elif isinstance(ast, unit):
        for tok in ast.value:
            verify(tok, symb, loc)
        
    elif isinstance(ast, vardecl):
        check_typename(ast.type)
        temp = find_tok(ast, ast.name, symb, loc)
        if ast.value:
            check_type(temp, ast.value, symb, loc)
            
    elif isinstance(ast, varassign):
        temp = find_tok(ast, ast.name, symb, loc)
        check_type(temp, ast.value, symb, loc)
            
    elif isinstance(ast, funcdecl):
        tloc = loc.copy()
        tloc.append(makeID())
        
        for tok in ast.body:
            verify(tok, symb, tloc)
        
    elif isinstance(ast, ifstate):
        tloc = loc.copy()
        tloc.append(makeID())
        
        for tok in ast.body:
            verify(tok, symb, tloc)
    
    elif isinstance(ast, whilestate):
        tloc = loc.copy()
        tloc.append(makeID())
        
        for tok in ast.body:
            verify(tok, symb, tloc)
            
    elif isinstance(ast, returnstate):
        if verify.cfunc.type.returns and ast.value:
            check_type(verify.cfunc.type.returns[0], ast.value, symb, loc) #TODO: only works with one return type
    
    elif isinstance(ast, funccall):
        temp = find_tok(ast, ast.name.value, symb, loc)
        
        if ast.args:
            if temp.type.generics:
                if len(ast.args) > len(temp.type.generics):
                    error(f"{ast.loc}: too many arguments for function '{temp.name}'")
                    
                for t, arg in zip(temp.type.generics, ast.args):
                    check_type(t, arg, symb, loc) 
