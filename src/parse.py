from cmath import exp
from email.policy import default
from src.common import *
import os
    
tok: token
    
def parse64(ltokens: list[token], verbose: bool) -> token:    
    """ parses a list of lexer tokens and returns the ast root token

    TODO: provide more information about what is stored in each tokens data based on the token type (information is stored in man/grammer.man)
    TODO: determine which parser to use, currently using a LL(k) parser, where k is commonly 1 (though not always)
    
    Args:
        ltokens (list[token]): list of lexer tokens
        verbose (bool): verbose output

    Returns:
        token: ast root token
    """    
    
    ltokens.reverse()
    out: token = 0
    
    def next():
        """ gets the next token from 'ltokens'
        """
        global tok
        if len(ltokens) > 0:
            tok = ltokens.pop()
        else:
            tok = None        
    
    def peek(loc: intl) -> token:
        """ gets the token at 'loc' from 'ltokens'
        
        Args:
            loc (int): location of the token to get
        
        Returns:
            token: token at 'loc' from 'ltokens'
        """ 
        if len(ltokens) >= loc:
            return ltokens[-loc]
        else: 
            return None
        
    def accept(typename) -> bool:
        """ checks if the next token is of a certain type and data, and calls 'next' if it is

        Args:
            type (Enum): type to check
            data (any, optional): specific data to check. Defaults to None.

        Returns:
            bool: true if the current token matches the type and data
        """             
        global tok
        if isinstance(tok, typename):
            next()
            return True
        return False
    
    def check(typename) -> bool:
        """ checks if the next token is of a certain type and data, does not call 'next'

        Args:
            type (Enum): type to check
            data (any, optional): specific data to check. Defaults to None.

        Returns:
            bool: true if the current token matches the type and data
        """     
        if isinstance(tok, typename):
            return True
        return False
    
    def expect(typename) -> bool:
        """ checks if the next token is of a certain type and data, and calls 'next' if it is, otherwise raises an error

        Args:
            type (Enum): type to check
            data (any, optional): specific data to check. Defaults to None.

        Returns:
            bool: true if the current token matches the type and data
        """        
        global tok 
        if accept(typename):
            return True
        else:
            error(f"{tok.loc}: expected {typename} got {type(tok)} instead.")
    
    def makeUnit() -> token:
        """ attemps to make a unit node, the base node for a single file
        
        TODO: add support for multiple files / include statements
        TODO: determine how to handle headers and precompiled files
        TODO: add makeDeclaration function and replace the code below with it
        TODO: classes / structs, enums, and unions
        TODO: determine if preprocessor directives should be handled here, and what directives should be supported
        
        Requires:
            LEXER.FILE
            ...
            LEXER.EOF

        Returns:
            token: ast root node
            error: if the tokens do not match the requirements
        """        
        global tok
        out = unit(tok.loc, [])
        expect(filel)
        pstack: list[token] = []
        
        while True:
            if tok is None:
                return error("parsing error, end of file never reached.")
            if check(eof):
                return out
            
            if check(id):
                current: id = tok
            
                # variable assignment
                if isinstance(peek(1), op) and peek(1).value in ["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^="]:
                    tpeek: op = peek(1)
                    out.value.append(makeVarAssign())
                        
                # struct
                elif current.value == "struct":
                    next()
                    out.value.append(makeStructDecl())
                    
                # var declaration
                else:
                    out.value.append(makeVarDecl())
                
            # class declaration
            elif False:
                out.value.append(makeClassDecl())
                
            else:
                error(f"{tok.loc}: unexpected token {tok}, expected declaration.")
            
        
        
        
    def assignstub() -> token:
        if check(group):
            current: group = tok
            if current.value in "[{":
                return makeFuncDecl()
        else:
            ret = makeExpr()
            expect(semi)
            return ret
        
    def makeVarDecl() -> token:
        """ attemps to make a variable declaration node

        TODO: multiple variable declaration and modifiers (static, const, etc.)

        Requires:
            LEXER.ID
            LEXER.ID
            ...
            LEXER.SEMI or LEXER.GROUP
                
        Returns:
            token: variable declaration node
            error: if the tokens do not match the requirements
        """
                
        loc = tok.loc
        type = makeType()
        name = ""
                
        if check(id):
            current: id = tok
            name = current.value
            next()
        else:
            error(f"{tok.loc}: expected variable name, got {tok} instead.")
        
        if accept(semi):
            return vardecl(loc, name, type)
        elif check(op) and tok.value in ["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^="]:
            next()
            return vardecl(loc, name, type, assignstub())
        else:
            error(f"{tok.loc}: expected ';', got {tok} instead.")
        
        
    
    def makeVarAssign() -> token:
        current: id = tok
        temp = varassign(current.loc, current.value, None, None)
        next()
        
        if not tok.value in ["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^="]:
            error(f"{tok.loc}: expected assignment operator, got {tok.type} {tok.data} instead.")
        
        current: op = tok 
        temp.oper = current.value
        
        next()
        temp.value = assignstub()
        
        return temp
    
    def makeClassDecl() -> token:
        todo("parse64", "makeClassDecl")
        
    def makeStructDecl() -> token:
        todo("parse64", "makeStructDecl")
        
    def funcstub() -> tuple[token, token]:
        name = None
        ret = None
        if check(id):
            current: id = tok
            name = current.value
            next()
            if check(op) and tok.value == "=":
                next()
                ret = makeExpr()
        else:
            error(f"{tok.loc}: expected identifier, got {tok} instead.")
           
        return (name, ret)
           
    def makeFuncDecl() -> token:
        """ attemps to make a function declaration node

        TODO: default arguments (e.g. [x = 0] => return x;)
        TODO: single line function declaration (e.g. [x] => return x;)
        TODO: simple return type inference (e.g. [x] => x; ) 
        TODO: inline calling (e.g. y => { if(x > 0) return x; return 0; }, same as func x = { if(x > 0) return x; return 0; } y = x(); )
        TODO: determine if above should be done in that way, or if it should be implemented at all

        Requires:
            ...
            LEXER.GROUP
            ...
            LEXER.GROUP

        Returns:
            token: function declaration node
            error: if the tokens do not match the requirements
        """        
        
        temp = funcdecl(tok.loc, None, None, None)
        
        arglist = []
        datlist = []
        default = []
        
        current: group = tok
        
        if current.value == "[":
            next()
            if check(id):
                t = funcstub()
                arglist.append(t[0])
                default.append(t[1])
                
            while accept(comma):
                t = funcstub()
                arglist.append(t[0])
                default.append(t[1])
                
            if check(group) and tok.value != "]":
                error(f"{tok.loc}: expected ']', got {tok} instead.")
                
            next()
         
        
        if check(group) and tok.value != "{":
            error(f"{tok.loc}: expected '" + '{' + f"', got {tok} instead.")
        
        next()
        
        while True:
            
            if check(group):
                if tok.value == "}":
                    next()
                    break
            
            if accept(eof):
                error(f"{temp.loc}: function definition expects closing brace, none found.")
            
            datlist.append(makeStatement())
            
        temp.args = arglist
        temp.body = datlist
        temp.dafualts = default
        
        return temp
    
    def makeStatement() -> token:
        """ attemps to make a statement node

        TODO: determine how to handle for loops
        TODO: goto?
        TODO: do while?
        TODO: switch and match statements
        
        Requires:
            ...

        Returns:
            token: statement node
            error: a matching statement node could not be made
        """        
        
        if accept(semi):
            return None
        
        elif check(id):
            current: id = tok
            if current.value == "if":
                return makeIfState()
            if current.value == "while":
                return makeWhileState()
            if current.value == "for":
                return makeForState()
            if current.value == "return":
                return makeReturnState()
            
            if isinstance(peek(1), op) and peek(1).value in ["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^="]:
                return makeVarAssign()
            if isinstance(peek(1), group) and peek(1).value in "(":
                return makeExpr()
            if isinstance(peek(1), id) or isinstance(peek(1), op) and peek(1).value == "<":
                return makeVarDecl()
            else:
                temp = makeExpr()
                expect(semi)
                return temp
        else:
            temp = makeExpr()
            expect(semi)
            return temp

    def makeType() -> token:
        """ attemps to make a type node

        TODO: the data contained in type nodes only contains id's, storing the entire token is unnecessary

        Requires:
            LEXER.ID
            ...
            
        Returns:
            token: type node
            error: if the tokens do not match the requirements
        """
                
        if check(id):
            temp = typep(tok.loc, tok.value)
            next()
        else:
            error(f"{tok.loc}: expected type, got {tok} instead.")
        
        argin  = []
        argout = []
        
        if check(op) and tok.value == "<":
            next()
            
            if check(op) and tok.value == ">":
                next()
                return temp
            
            argin.append(makeType())
            
            while accept(comma):
                argin.append(makeType())
                
            if check(op) and tok.value == "->":
                next()
                
                argout.append(makeType())
                
                while accept(comma):
                    argout.append(makeType())
                    
                if check(op) and tok.value == ">":
                    next()
                else:
                    error(f"{tok.loc}: type expects '>', got {tok} instead.")
            
            elif check(op) and tok.value == ">":
                next()
                
            else:
                error(f"{tok.loc}: type expects '>', got {tok} instead.")
                
        print(argin)
                
        if len(argin) > 0:
            temp.generics = argin
        if len(argout) > 0:
            temp.returns = argout
            
        return temp
    
    def makeExpr() -> token:
        """ attemps to make an expression node

        TODO: some expressions keep thier base tokens, others do not, this should be consistent
        TODO: ternary operator (and other compound expressions) 

        Returns:
            token: expression node
            error: if an expression node could not be made
        """        
        return makeConditional()
        
    def bodystub() -> list[token]:
        retlist = []
        
        if check(group) and tok.value == "{":
            next()
            while True:
                if check(group):
                    if tok.value == "}":
                        next()
                        break
                
                if accept(eof):
                    error(f"{tok.loc}: if statement expects closing brace, none found.")
                
                t = makeStatement()
                if t:
                    retlist.append(t)
            
        else:
            t = makeStatement()
            if t:
                retlist.append(t)
            
        return retlist
        
    def makeIfState() -> token:
        """ attemps to make an if statement node

        TODO: determine if this should be handled in this way
        TODO: extract repeated code into a function

        Requires:
            LEXER.ID
            ...

        Returns:
            token: if statement node
            error: if the tokens do not match the requirements
        """
        temp = ifstate(tok.loc, None, None, None, None)
        eliflist = []
        
        next()
        if check(group) and tok.value == "(":
            next()
            temp.cond = makeExpr()
        else:
            error(f"{tok.loc}: if statement expects '(', got {tok} instead.")
        if check(group) and tok.value == ")":
            next()
        else:
            error(f"{tok.loc}: if statement expects ')', got {tok} instead.")
        
        temp.body = bodystub()
        
        while check(id) and tok.value == "else" and isinstance(peek(1), id) and peek(1).value == "if":
            next()
            next()
            temp2 = ifstate(tok.loc, None, None, None, None)
            
            if check(group) and tok.value == "(":
                next()
                temp2.cond = makeExpr()
            else:
                error(f"{tok.loc}: if statement expects '(', got {tok} instead.")
            if check(group) and tok.value == ")":
                next()
            else:
                error(f"{tok.loc}: if statement expects ')', got {tok} instead.")
            
            temp2.body = bodystub()
        
            eliflist.append(temp2)
        
        if check(id) and tok.value == "else":
            next()
            temp.elsebody = bodystub()
        
        temp.ifelse = eliflist
        
        return temp
    
    def makeWhileState() -> token:
        """ attemps to make a while statement node

        TODO: do while?

        Requires:
            LEXER.ID
            ...

        Returns:
            token: while statement node
        """        
        temp = whilestate(tok.loc, None, None)
        next()
        
        if check(group) and tok.value == "(":
            next()
            temp.cond = makeExpr()
        else:
            error(f"{tok.loc}: if statement expects '(', got {tok} instead.")
        if check(group) and tok.value == ")":
            next()
        else:
            error(f"{tok.loc}: if statement expects ')', got {tok} instead.")
        
        temp.body = bodystub()
        
        return temp
    
    def makeForState() -> token:
        todo("parse64", "makeFor")
    
    def makeReturnState() -> token:
        """ attemps to make a return statement node

        TODO: multiple return values

        Requires:
            LEXER.ID
            ...
            LEXER.SEMI
    
        Returns:
            token: return statement node
        """
        
        temp = returnstate(tok.loc, None)       
        next()
        if accept(semi):
            return temp
        
        temp.value = makeExpr()
        expect(semi)
        return temp
        
    def makeConditional() -> token:
        
        temp = makeBitwise()
        
        while check(op) and tok.value in ["==", "!=", "<", ">", "<=", ">=", "||", "&&"]:
            oper = tok.value
            next()
            temp = expr(tok.loc, oper, temp, makeBitwise())
        
        return temp      
    
    def makeBitwise() -> token:
        temp = makeSummand()
            
        while check(op) and tok.value in ["&", "|", "^", "<", ">"]:
            if check(op) and tok.value == "<" and isinstance(peek(1), op) and peek(1).value == "<":
                next()
                next()
                temp = expr(tok.loc, "<<", temp, makeSummand())
            elif check(op) and tok.value == ">" and isinstance(peek(1), op) and peek(1).value == ">":
                next()
                next()
                temp = expr(tok.loc, ">>", temp, makeSummand())
            elif check(op) and tok.value in ["<", ">"]:
                break
            else:
                oper = tok.value
                next()
                temp = expr(tok.loc, oper, temp, makeSummand())
            
        return temp
    
    def makeSummand() -> token:
        temp = makeFactor()
        while check(op) and tok.value in ["+", "-"]:
            oper = tok.value
            next()
            temp = expr(tok.loc, oper, temp, makeFactor())
        return temp    
     
    def makeFactor() -> token:
        temp = makeUnary()
        while check(op) and tok.value in ["*", "/", "%"]:
            oper = tok.value
            next()
            temp = expr(tok.loc, oper, temp, makeUnary())
        return temp   
         
    def makeUnary() -> token:
        
        if check(op) and tok.value in ["+", "-", "~", "!", "*", "&", "++", "--"]:
            oper = tok.value
            if oper in ["++", "--"]:
                oper = "l" + oper
            if oper in ["*", "&", "-", "+"]:
                oper = "u" + oper
            next()
            return expr(tok.loc, oper, makeUnary(), None)
        else:
            temp = makeValue()
            
            if check(op) and tok.value in ["++", "--"]:
                oper = "r" + tok.value
                next()
                return expr(tok.loc, oper, temp, None)
            else:
                return temp       
               
    def makeValue() -> token:
        temp = tok
        if check(group) and tok.value == "(":
            temp = makeExpr()
            if check(group) and tok.value == ")":
                next()
            else:
                error(f"{tok.loc}: expected ')', got {tok} instead.")
            return temp
        elif accept(intl):
            return temp
        elif accept(floatl):
            return temp
        elif accept(stringl):
            return temp
        elif accept(charl):
            return temp
        elif accept(booll):
            return temp
        elif accept(id):
            
            if check(group) and tok.value == "(":
                temp = funccall(tok.loc, temp, None)
                next()
                
                if check(group) and tok.value == ")":
                    next()
                    return temp
                else:
                    arglist = []
                    
                    while True:
                        arglist.append(makeExpr())
                        if accept(comma):
                            continue
                        elif check(group) and tok.value == ")":
                            next()
                            break
                        else:
                            error(f"{tok.loc}: expected ')' or ',', got {tok} instead.")
                    
                    temp.args = arglist
                    return temp
                
            elif check(op) and tok.value == "[":
                next()
                temp = index(tok.loc, temp, makeExpr())
                if check(op) and tok.value == "]":
                    next()
                    return temp
                else:
                    error(f"{tok.loc}: expected ']', got {tok} instead.")
            elif check(op) and tok.value == ".":
                next()
                if check(id):
                    temp = member(tok.loc, temp, tok)
                    next()
                    return temp
                else:
                    error(f"{tok.loc}: expected identifier, got {tok} instead.")
            else:
                return temp
        else:
            error(f"{tok.loc}: expected value, got {tok} instead.")
            
    next()
    out = makeUnit()
    
    if verbose:
        
        if not os.path.exists(".test"):
            os.mkdir(".test")
            print(" -> [PARSER]: created directory '.test'")
        
        if not os.path.exists(".test/parse"):
            os.mkdir(".test/parse")
            print(" -> [PARSER]: created directory '.test/parse'")
        
        t = str(out)
        with open(".test/parse/" + out.loc.file.split("/")[-1], "w") as f:
            f.write(t)
        print(" -> [PARSER]: AST written to " + ".test/parse/" + out.loc.file.split("/")[-1])
            
    return out
