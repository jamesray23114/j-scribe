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
    
    
    if verbose:
        if not os.path.exists(".test"):
            os.mkdir(".test")
            print(" -> [LEXER]: created .text directory")
            
        if not os.path.exists(".test/analysis"):
            os.mkdir(".test/analysis")
            print(" -> [LEXER]: created .test/analysis directory")
            
        with open(".test/analysis/" + "symb_" + ast.loc.file.split("/")[-1], "w") as file:
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
        
        print(" -> [LEXER]: wrote tokens to .test/analysis/" + "symb_" + ast.loc.file.split("/")[-1])

            
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
    
    todo("analyze64", "finish this function")
    
    makeID.val = 0
    verf = verify(ast, symb)
    
    todo("analyze64", "analyze")
    
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
        return typep(glb, [id(glb, type)], generics, returns)
    elif generics != [] and returns == []:
        return typep(glb, [id(glb, type)], generics)
    else:
        return typep(glb, [id(glb, type)])
    
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
        
        functions.append(function(curr.loc, tloc, makeID(), curr.args, curr.dafualts))
        
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



# def find_tok(tok: token, symb: tuple[list[token], list[token]], loc: list[intl]) -> token:
#     """ 
#         returns a token from the symbol table whose id matches 'tok' and
#         ensures the token has no duplicates + exists in the current scope
        
#         TODO: determine if this is the best way to do this (e.g. should the symbol table be sorted?)
        
#         Args:
#             tok (token):  the id token whose name is searched for
#             symb (tuple): the symbol table
#             loc (list[int]):  the current scope
        
#         Returns:
#             token: the token from the symbol table
#             error: halts the program if the token is not found or duplicates are found
#     """
#     out = 0
#     main = 0
    
#     for var in symb[1]:
        
#         if var.data[3].data == tok.data:
#             if not check_scope(var, loc):
#                 continue
            
#             if var.data[3].data == "main" and main == 0:
#                 main = var
                
#             elif out == 0:
#                 out = var
#             else:
#                 error(f"{tok.loc}: variable '{tok.data}' has duplicate definitions")
    
#     if main != 0:
#         out = main
    
#     if out == 0:
#         error(f"{tok.loc}: variable '{tok.data}' is not defined")
    
#     return out

# def check_scope(tok: token, loc: list[intl]) -> bool:
#     """ verifies that the token is in the current scope 

#     Args:
#         tok (token): the token to check
#         loc (list[int]): the current scope

#     Returns:
#         bool: true if token is in the current scope, false otherwise
#     """
    
#     if loc == [] and tok.data[0] != []:
#         return False
    
#     if tok.data[0] == []:
#         return True
    
#     for i in range(len(loc)):
#         if tok.data[0][i] != loc[i]:
#             return False
    
#     return True

# def check_type(t: token, compare: token) -> bool:
    
#     if t.type != PARSER.TYPE:
#         error(f"{t.loc}: type expected, got {t.type} instead")
        
#     typename = t.data[0].data
    
#     if typename == "int":
#         if compare.type == LEXER.INT:
#             return True
#         else:
#             error(f"{compare.loc}: type mismatch, expected {typename}, got {compare.type} instead")

#     elif typename == "float":
#         if compare.type == LEXER.FLOAT:
#             return True
#         else:
#             error(f"{compare.loc}: type mismatch, expected {typename}, got {compare.type} instead")
            
#     elif typename == "char":
#         if compare.type == LEXER.CHAR:
#             return True
#         else:
#             error(f"{compare.loc}: type mismatch, expected {typename}, got {compare.type} instead")
            
#     elif typename == "string":
#         if compare.type == LEXER.STRING:
#             return True
#         else:
#             error(f"{compare.loc}: type mismatch, expected {typename}, got {compare.type} instead")
            
#     elif typename == "bool":
#         if compare.type == PARSER.BOOL:
#             return True
#         else:
#             error(f"{compare.loc}: type mismatch, expected {typename}, got {compare.type} instead")
            
#     elif typename == "void":
#         todo("check_type", "void")

#     elif typename == "ptr":
#         todo("check_type", "ptr")
        
#     elif typename == "func":
#         if compare.type == PARSER.FUNCDECL:
            
#             if len(t.data[1]) < len(compare.data[0]):
#                 error(f"{compare.loc}: too many arguments, function expects {len(t.data[1])} argument(s) but got {len(compare.data[0])} instead")
            
#             if len(t.data[2]) > 1:
#                 todo("check_type", "function with multiple return values")
            
#             return True
            
#         else:
#             error(f"{compare.loc}: type mismatch, expected {typename}, got {compare.type} instead")
        
#     else:
#         error(f"{t.loc}: unknown type '{typename}'")
        
# def check_typename(tok: token):
#     """ checks if the 'type' token has a valid type name

#     TODO: custom types

#     Args:
#         tok (token): the token to check, must be of type PARSER.TYPE

#     Returns:
#         bool: returns true if the type name is valid
#         error: halts program on error
#     """


#     stypes = [ #simple types
#         "int",
#         "bool",
#         "string",
#         "char",
#         "float",
#         "void"
#     ]

#     ctypes = [ #complex types
#         "ptr",
#         "func"
#     ]

    
#     if tok.data[0].data in stypes:
#         if len(tok.data) == 1:
#             return 
#         else:
#             error(f"{tok.loc}: type '{tok.data[0].data}' cannot have modifiers")
    
#     elif tok.data[0].data in ctypes:
#         if len(tok.data) == 2:
#             for t in tok.data[1]:
#                 check_typename(t)
#             return 
#         elif len(tok.data) == 3:
            
#             if tok.data[0].data == "ptr":
#                 error(f"{tok.loc}: pointer type cannot have return types")
            
#             for t in tok.data[1]:
#                 check_typename(t)
#             for t in tok.data[2]:
#                 check_typename(t)
#             return 
#         else:
#             return 
#     error(f"{tok.loc}: invalid type '{tok.data[0].data}'")
 
# def verify(ast: token, symb: tuple[list[token], list[token]], loc: list[intl] = []):
#     """ verifies the syntax of the program

#     TODO: finish this

#     Args:
#         ast (token): the abstract syntax tree
#         symb (tuple): the symbol table
#         loc (list[int]: the current scope, used internally. Defaults to [].

#     Returns:
#         token: ?
#     """    
    
#     if ast.type == PARSER.UNIT:
#         for tok in ast.data:
#             ast = verify(tok, symb, loc)
    
#     elif ast.type == PARSER.PREPROC:
#         pass
    
#     elif ast.type == PARSER.VARDECL:
#         makeID()
        
#         check_typename(ast.data[0])
#         tok = find_tok(ast.data[1], symb, loc)
        
#         return       
            
#     elif ast.type == PARSER.FUNCDECL:
#         makeID()
#         todo("verify", "verify funcdecl") 
#             # [ ] check if arglist matches
            
#     elif ast.type == PARSER.VARASSIGN:
        
#         temp = find_tok(ast.data[0], symb, loc)
        
#         check_type(temp.data[2], ast.data[2])
        
#         todo("verify", "verify varassign")
#             # [x] check if id exists
#             # [x] check if id is in scope
#             # [ ] check if type matches
            
#     elif ast.type == PARSER.IF:
#         makeID()
#         todo("verify", "verify if")
#             # [ ] check if expression is bool
#             # [ ] check if expression (vars) is in scope
    
#     elif ast.type == PARSER.WHILE:
#         makeID()
#         todo("verify", "verify while")
#             # [ ] check if expression is bool
#             # [ ] check if expression (vars) is in scope
            
#     elif ast.type == PARSER.EXPR:
#         todo("verify", "verify expr")
#             # [ ] check if expression is valid
#             # [ ] check if expression (vars) is in scope
            
#     elif ast.type == PARSER.RETURN:
#         todo("verify", "verify return")
#             # [ ] check if return type matches
            
#     elif ast.type == PARSER.TYPE:
#         todo("verify", "verify type")
#             # [ ] check if type is valid
    
#     pass
