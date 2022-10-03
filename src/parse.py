from src.common import *
import os
    
tok: token = None
    
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
    
    def peek(loc: int) -> token:
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
        
    def accept(type: Enum, data: any = None) -> bool:
        """ checks if the next token is of a certain type and data, and calls 'next' if it is

        Args:
            type (Enum): type to check
            data (any, optional): specific data to check. Defaults to None.

        Returns:
            bool: true if the current token matches the type and data
        """             
        global tok 
        if tok.type == type:
            if data is None:
                next()
                return True
            elif tok.data == data:
                next()
                return True
        return False
    
    def check(type: Enum, data: any = None) -> bool:
        """ checks if the next token is of a certain type and data, does not call 'next'

        Args:
            type (Enum): type to check
            data (any, optional): specific data to check. Defaults to None.

        Returns:
            bool: true if the current token matches the type and data
        """     
        if tok.type == type:
            if data is None:
                return True
            elif tok.data == data:
                return True
        return False
    
    def expect(type: Enum, data: any = None) -> bool:
        """ checks if the next token is of a certain type and data, and calls 'next' if it is, otherwise raises an error

        Args:
            type (Enum): type to check
            data (any, optional): specific data to check. Defaults to None.

        Returns:
            bool: true if the current token matches the type and data
        """        
        global tok 
        if accept(type, data):
            return True
        if data is None:
            error(f"{tok.loc}: expected {type}, got {tok.type} instead.")
        else:
            error(f"{tok.loc}: expected {type} {data}, got {tok.type} {tok.data} instead.")
    
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
        out = token(tok.loc, PARSER.UNIT, None)
        expect (LEXER.FILE)
        pstack: list[token] = []
        
        while True:
            if tok is None:
                return error("parsing error, end of file never reached.")
            if tok.type == LEXER.EOF:
                out.data = pstack
                return out
            
            temp = None
            
            # variable assignment
            if check(LEXER.ID) and peek(1) == LEXER.OP and peek(1).data in ["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^="]:
                temp = makeVarAssign()
                
            # variable declaration
            elif check(LEXER.ID):
                temp = makeVarDecl()
                if peek(1) == LEXER.OP and peek(1).data in ["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^="]:
                    pstack.append(temp)
                    if temp.data[1] == LEXER.ID:
                        temp = makeVarAssign()
                    else:
                        error(f"{tok.loc}: expected variable name, got {tok.type} {tok.data} instead.")
                    
                else:
                    next()
                    expect(LEXER.SEMI)
            # function declaration
            elif check(LEXER.GROUP, "{") or check(LEXER.GROUP, "["):
                temp = makeFuncDecl()
                
            # class declaration
            elif False:
                temp = makeClassDecl()
                
            # preprocessor
            elif accept(LEXER.HASH):
                temp = makePreProc()
            
            else:
                error(f"{tok.loc}: unexpected token {tok.type} {tok.data}, expected declaration.")
            
            if temp is not None:
                pstack.append(temp)
        
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
        temp = token(tok.loc, PARSER.VARDECL, [makeType()])
        if check(LEXER.ID):
            temp.data.append(tok)
        else:
            error(f"{tok.loc}: expected variable name, got {tok.type} {tok.data} instead.")
        return temp
    def makeVarAssign() -> token:
        temp = token(tok.loc, PARSER.VARASSIGN, [tok])
        next()
        
        temp.data.append(tok.data)
        if not tok.data in ["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^="]:
            error(f"{tok.loc}: expected assignment operator, got {tok.type} {tok.data} instead.")
        next()
        
        if check(LEXER.GROUP, "{") or check(LEXER.GROUP, "["):
            temp.data.append(makeFuncDecl())
        else:
            temp.data.append(makeExpr())
            expect(LEXER.SEMI)
        
        return temp
    
    def makeClassDecl() -> token:
        todo("parse64", "makeClassDecl")
        
    def makePreProc() -> token:
        """ attemps to make a preprocessor node

        TODO: the variability of preprocessor directives makes it difficult to parse them, different directives should be parsed in their own functions
        TODO: include directives should be parsed and lexed in thier respective stages, not after 
        
        Requires:
            LEXER.HASH
            LEXER.ID
            ...
            LEXER.SEMI

        Returns:
            token: preprocessor node
            error: if the tokens do not match the requirements
        """       
         
        temp = token(tok.loc, PARSER.PREPROC, [ tok ])
        expect(LEXER.ID)
        while True:
            temp.data.append(tok)
            next()
            if tok is None:
                return error(f"parsing error {temp.loc} preprocessor expects semicolon, found none.")
            if accept(LEXER.SEMI):
                return temp
            expect(LEXER.COMMA)
            
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
        
        temp = token(tok.loc, PARSER.FUNCDECL, [])
        
        arglist = []
        datlist = []
        
        if accept(LEXER.GROUP, "["):
            
            if check(LEXER.ID):
                arglist.append(tok.data)
                next()
            
            while not accept(LEXER.GROUP, "]"):
                if accept(LEXER.EOF):
                    error(f"{tok.loc}: function definition expects closing bracket, none found.")

                expect(LEXER.COMMA)
                
                if check(LEXER.ID):
                    arglist.append(tok.data)
                    next()
                else:
                    error(f"{tok.loc}: expected argument name, got {tok.type} {tok.data} instead.")
         
        expect(LEXER.GROUP, "{")
        
        while not accept(LEXER.GROUP, "}"):
            if accept(LEXER.EOF):
                error(f"{temp.loc}: function definition expects closing brace, none found.")
                
            datlist.append(makeStatement())
            
        temp.data.append(arglist)
        temp.data.append(datlist)
        
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
        
        if accept(LEXER.SEMI):
            return None
        if accept(LEXER.HASH):
            return makePreProc()
        elif check(LEXER.ID) and peek(1) == LEXER.OP and peek(1).data in ["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^="]:
            return makeVarAssign()
        elif accept(LEXER.ID, "if"):
            return makeIfState()
        elif accept(LEXER.ID, "for"):
            return makeForState()
        elif accept(LEXER.ID, "while"):
            return makeWhileState()
        elif accept(LEXER.ID, "return"):
            return makeReturn()
        elif check(LEXER.ID):
            
            if peek(1) == LEXER.ID or (peek(1) == LEXER.OP and peek(1).data == "<"):
                temp = makeVarDecl()
                if peek(1) == LEXER.OP and peek(1).data in ["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^="]:
                    pass
                else:
                    next()
                    expect(LEXER.SEMI)
                return temp
                
            else:
                temp = makeExpr()
                expect(LEXER.SEMI)
                return temp
        else:
            temp = makeExpr()
            expect(LEXER.SEMI)
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
        if check(LEXER.ID):
            temp = token(tok.loc, PARSER.TYPE, [ tok ])
            next()
        else:
            return None
        
        isout = False
        argin  = []
        argout = []
        
        if (accept(LEXER.OP, "<")):
            
            
            if accept(LEXER.OP, ">"):
                return temp
            
            argin.append(makeType())
            
            while not accept(LEXER.OP, ">"):
                if accept(LEXER.EOF):
                    error(f"{temp.loc}: expected closing angle bracket, found none.")
                if accept(LEXER.OP, "->"):
                    if isout:
                        error(f"{tok.loc}: unexpected token \"->\".")
                    isout = True
                    argout.append(makeType())
                else:
                    expect(LEXER.COMMA)
                    if isout:
                        argout.append(makeType())
                    else:
                        argin.append(makeType())
                
            
        if argin != []:
            temp.data.append(argin)
        if argout != []:
            temp.data.append(argout)
            
        return temp
    
    def makeExpr() -> token:
        """ attemps to make an expression node

        TODO: some expressions keep thier base tokens, others do not, this should be consistent
        TODO: ternary operator (and other compound expressions) 

        Returns:
            token: expression node
            error: if an expression node could not be made
        """        
        if accept(LEXER.ID, "true"):
            return token(tok.loc, PARSER.BOOL, "true")
        elif accept(LEXER.ID, "false"):
            return token(tok.loc, PARSER.BOOL, "false")
        else:
            temp = makeConditional()
            return temp
        
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
        temp = token(tok.loc, PARSER.IF, [])
        
        datlist = []
        eliflist = []
        elselist = []
        
        expect(LEXER.GROUP, "(")
        temp.data.append(makeExpr())
        expect(LEXER.GROUP, ")")
        
        if accept(LEXER.GROUP, "{"):
            while not accept(LEXER.GROUP, "}"):
                if accept(LEXER.EOF):
                    error(f"{tok.loc}: if statement expects closing brace, none found.")
                t = makeStatement()
                if t is not None:
                    datlist.append(t)
        else:
            t = makeStatement()
            if t is not None:
                datlist.append(t)
        
        while accept(LEXER.ID, "else"):
            
            if accept(LEXER.ID, "if"):
                
                temp1 = token(tok.loc, PARSER.IF, [])
                datlist1 = []
                
                expect(LEXER.GROUP, "(")
                temp1.data.append(makeExpr())
                expect(LEXER.GROUP, ")")
                
                if accept(LEXER.GROUP, "{"):
                    while not accept(LEXER.GROUP, "}"):
                        if accept(LEXER.EOF):
                            error(f"{tok.loc}: if statement expects closing brace, none found.")
                        t = makeStatement()
                        if t is not None:
                            datlist1.append(makeStatement())
                else:
                    t = makeStatement()
                    if t is not None:
                        datlist1.append(t)
                
                temp1.data.append(datlist1)
                eliflist.append(temp1)
                
            else:
                if accept(LEXER.GROUP, "{"):
                    while not accept(LEXER.GROUP, "}"):
                        if accept(LEXER.EOF):
                            error(f"{tok.loc}: else statement expects closing brace, none found.")
                        t = makeStatement()
                        if t is not None:
                            elselist.append(t)
                else:
                    t = makeStatement()
                    if t is not None:
                        elselist.append(t)  
        
        temp.data.append(datlist)
        if elselist != []:
            temp.data.append(eliflist)
            temp.data.append(elselist)
        elif eliflist != []:
            temp.data.append(eliflist)
        
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
        temp = token(tok.loc, PARSER.WHILE, [])
        
        datlist = []
        
        expect(LEXER.GROUP, "(")
        temp.data.append(makeExpr())
        expect(LEXER.GROUP, ")")
        
        if accept(LEXER.GROUP, "{"):
            while not accept(LEXER.GROUP, "}"):
                if accept(LEXER.EOF):
                    error(f"{tok.loc}: while statement expects closing brace, none found.")
                datlist.append(makeStatement())
        else:
            datlist.append(makeStatement())
        
        temp.data.append(datlist)
        
        return temp
    
    def makeForState() -> token:
        todo("parse64", "makeFor")
    
    def makeReturn() -> token:
        """ attemps to make a return statement node

        TODO: multiple return values

        Requires:
            LEXER.ID
            ...
            LEXER.SEMI
    
        Returns:
            token: return statement node
        """        
        temp = token(tok.loc, PARSER.RETURN, None)
        if accept(LEXER.SEMI):
            return temp
        temp.data = makeExpr()
        expect(LEXER.SEMI)
        return temp
        
    def makeConditional() -> token:
        
        temp = makeLogic()
        
        while check(LEXER.OP, "==") or check(LEXER.OP, "!=") or check(LEXER.OP, "<") or check(LEXER.OP, ">") or check(LEXER.OP, "<=") or check(LEXER.OP, ">=") or check(LEXER.ID, "||") or check(LEXER.ID, "&&"):
            op = tok.data
            next()
            temp = token(tok.loc, PARSER.CONDITION, [op, temp, makeLogic()])
        
        return temp      
    
    def makeLogic() -> token:
        temp = makeSummand()
        
        while check(LEXER.OP, "&") or check(LEXER.OP, "|") or check(LEXER.OP, "^") or check(LEXER.OP, "<") or check(LEXER.OP, ">"):
            if check(LEXER.OP, "<") and peek(1) == LEXER.OP and peek(1).data == "<":
                next()
                next()
                temp = token(tok.loc, PARSER.EXPR, ["<<", temp, makeSummand()])
            elif check(LEXER.OP, ">") and peek(1) == LEXER.OP and peek(1).data == ">":
                next()
                next()
                temp = token(tok.loc, PARSER.EXPR, [">>", temp, makeSummand()])
            elif check(LEXER.OP, "<") or check(LEXER.OP, ">"):
                break
            else:    
                op = tok.data
                next()
                temp = token(temp.loc, PARSER.EXPR, [op, temp, makeSummand()])
            
        return temp
    
    def makeSummand() -> token:
        temp = makeFactor()
        while check(LEXER.OP, "+") or check(LEXER.OP, "-"):
            op = tok.data
            next()
            temp = token(temp.loc, PARSER.EXPR, [op, temp, makeFactor()])
        return temp    
     
    def makeFactor() -> token:
        temp = makeUnary()
        while check(LEXER.OP, "*") or check(LEXER.OP, "/") or check(LEXER.OP, "%"):
            op = tok.data
            next()
            temp = token(temp.loc, PARSER.EXPR, [op, temp, makeUnary()])
        return temp   
         
    def makeUnary() -> token:
        if accept(LEXER.OP, "!"):
            temp = makeValue()
            return token(tok.loc, PARSER.EXPR, ["!", temp])
        elif accept(LEXER.OP, "*"):
            temp = makeValue()
            return token(tok.loc, PARSER.EXPR, ["u*", temp])
        elif accept(LEXER.OP, "&"):
            temp = makeValue()
            return token(tok.loc, PARSER.EXPR, ["u&", temp])
        elif accept(LEXER.OP, "-"):
            temp = makeValue()
            return token(tok.loc, PARSER.EXPR, ["u-", temp])
        elif accept(LEXER.OP, "~"):
            temp = makeValue()
            return token(tok.loc, PARSER.EXPR, ["~", temp])
        elif accept(LEXER.OP, "++"):
            temp = makeValue()
            return token(tok.loc, PARSER.EXPR, ["l++", temp])
        elif accept(LEXER.OP, "--"):
            temp = makeValue()
            return token(tok.loc, PARSER.EXPR, ["l--", temp])
        else:
            temp = makeValue()
            if accept(LEXER.OP, "++"):
                return token(tok.loc, PARSER.EXPR, ["r++", temp])
            elif accept(LEXER.OP, "--"):
                return token(tok.loc, PARSER.EXPR, ["r--", temp])
            else:
                return temp       
               
    def makeValue() -> token:
        temp = tok
        if accept(LEXER.GROUP, "("):
            temp = makeExpr()
            expect(LEXER.GROUP, ")")
            return temp
        elif accept(LEXER.INT):
            return temp
        elif accept(LEXER.FLOAT):
            return temp
        elif accept(LEXER.STRING):
            return temp
        elif accept(LEXER.CHAR):
            return temp
        elif accept(LEXER.ID):
            if accept(LEXER.GROUP, "("):
                temp = token(tok.loc, PARSER.FUNCCALL, [temp.data])
                if not accept(LEXER.GROUP, ")"):
                    temp.data.append(makeExpr())
                    while accept(LEXER.COMMA):
                        temp.data.append(makeExpr())
                    expect(LEXER.GROUP, ")")
                return temp
            elif accept(LEXER.GROUP, "["):
                temp = token(tok.loc, PARSER.INDEX, [temp.data, makeExpr()])
                expect(LEXER.GROUP, "]")
                return temp
            elif accept(LEXER.OP, "."):
                temp = token(tok.loc, PARSER.MEMBER, [temp.data, makeValue()])
                return temp
            else:
                return temp
        else:
            error(f"{tok.loc}: expected value, got {tok.type} instead.")
            
    next()
    out = makeUnit()
    
    if verbose:
        
        if not os.path.exists(".test"):
            os.mkdir(".test")
            print(" -> [PARSER]: created directory '.test'")
        
        if not os.path.exists(".test/parse"):
            os.mkdir(".test/parse")
            print(" -> [PARSER]: created directory '.test/parse'")
        
        t = printAst(out)
        with open(".test/parse/" + out.loc.file.split("/")[-1], "w") as f:
            f.write("{\n")
            f.write(t)
            f.write("}")
        print(" -> [PARSER]: AST written to " + ".test/parse/" + out.loc.file.split("/")[-1])
            
    return out

def printAst(ast: token, depth: int = 1) -> str:
    """ returns a string representation of the AST

    TODO: completely redo this function
    TODO: dont use json, use a custom format. json makes it hard to read because of indentation
    TODO: determine if another format would be better, or if plain text would be better
    TODO: less repetition

    Args:
        ast (token): the root node of the AST
        depth (int, optional): the amount of tabs to print, used internally. Defaults to 1.

    Returns:
        str: the string representation of the AST
    """    
    
    out = ""
    
        
    if type(ast) is token:
        
        
        if ast.type == LEXER.INT:
            out += str(ast.data) 
        elif ast.type == LEXER.FLOAT:
            out += str(ast.data)    
        elif ast.type == LEXER.STRING or ast.type == LEXER.ID:
            out += "\"" + ast.data + "\""
        elif ast.type == LEXER.CHAR:
            out += "\'" + ast.data + "\'"
        elif ast.type == PARSER.BOOL:
            out += str(ast.data).lower()

        elif ast.type == PARSER.TYPE:
            out += "{\n"
            out += "\t" * (depth + 1)
            out += "\"name\": " + printAst(ast.data[0], depth + 2) + "\n"
            out += "\t" * (depth)
            out += "}"
            

        elif ast.type == PARSER.EXPR:
            out += "\t" * depth
            out += "\"expression\": {\n"
            out += "\t" * (depth + 1)
            out += "\"location\": \"" + str(ast.loc) + "\",\n"
            out += "\t" * (depth + 1)
            out += "\"operator\": \"" + str(ast.data[0]) + "\",\n"
            out += "\t" * (depth + 1)
            out += "\"left\": "
            
            if  ast.data[1].type == PARSER.EXPR:
                out += "{\n"
                out += printAst(ast.data[1], depth + 2)
                out += "\t" * (depth + 1)
                out += "}"
            else:
                out += printAst(ast.data[1], depth + 2)
            
            
            if len(ast.data) > 2:
            
                out += ",\n"
                out += "\t" * (depth + 1)
                out += "\"right\": "
                if ast.data[2].type == PARSER.EXPR:
                    out += "{\n"
                    out += printAst(ast.data[2], depth + 2)
                    out += "\t" * (depth + 1)
                    out += "}"
                else:
                    out += printAst(ast.data[2], depth + 2)
            
            out += "\n"
            out += "\t" * depth
            out += "}"
        elif ast.type == PARSER.CONDITION:
            out += "\t" * depth
            out += "\"condition\": {\n"
            out += "\t" * (depth + 1)
            out += "\"location\": \"" + str(ast.loc) + "\",\n"
            out += "\t" * (depth + 1)
            out += "\"operator\": \"" + str(ast.data[0]) + "\",\n"
            out += "\t" * (depth + 1)
            out += "\"left\": "
            
            if  ast.data[1].type == PARSER.EXPR:
                out += "{\n"
                out += printAst(ast.data[1], depth + 2)
                out += "\t" * (depth + 1)
                out += "}"
            else:
                out += printAst(ast.data[1], depth + 2)
            
            out += ",\n"
            out += "\t" * (depth + 1)
            out += "\"right\": "
            
            if ast.data[2].type == PARSER.EXPR:
                out += "{\n"
                out += printAst(ast.data[2], depth + 2)
                out += "\t" * (depth + 1)
                out += "}"
            else:
                out += printAst(ast.data[2], depth + 2)
            
            out += "\n"
            out += "\t" * depth
            out += "}\n"
            
        elif ast.type == PARSER.UNIT:
            out += "\t" * depth 
            out += "\"unit\": {\n"
            out += "\t" * (depth + 1) 
            out += "\"location\": \"" + str(ast.loc) + "\",\n"
            out += "\t" * (depth + 1)
            out += "\"program\": [\n"
            out += printAst(ast.data, depth + 2)
            out += "\t" * (depth + 1) 
            out += "]\n"
            out += "\t" * depth 
            out += "}\n"                 
        elif ast.type == PARSER.PREPROC:
            out += "\t" * depth 
            out += "\"preproc\": {\n"
            out += "\t" * (depth + 1) 
            out += "\"location\": \" " + str(ast.loc) + "\",\n"
            out += "\t" * (depth + 1)
            out += "\"directive\":" + printAst(ast.data[0]) + ",\n"
            out += "\t" * (depth + 1)
            out += "\"args\": [\n"
            
            i = 1
            while i < len(ast.data):
                out += "\t" * (depth + 2)
                out += printAst(ast.data[i], depth + 2)
                if i + 1 < len(ast.data):
                    out += ",\n"
                else:
                    out += "\n"
                i += 1
                
            
            out += "\t" * (depth + 1) 
            out += "]\n"
            out += "\t" * depth 
            out += "}"     
        elif ast.type == PARSER.VARDECL:
            out += "\t" * depth 
            out += "\"vardecl\": {\n"
            out += "\t" * (depth + 1) 
            out += "\"location\": \"" + str(ast.loc) + "\",\n"
            out += "\t" * (depth + 1)
            out += "\"type\": " + printAst(ast.data[0], depth + 1) + ",\n"
            out += "\t" * (depth + 1)
            out += "\"name\": " + printAst(ast.data[1], depth + 1) + "\n"
            out += "\t" * depth 
            out += "}"
        elif ast.type == PARSER.FUNCDECL:
            out += "\t" * depth
            out += "\"funcdecl\": {\n"
            out += "\t" * (depth + 1)
            out += "\"location\": \"" + str(ast.loc) + "\",\n"
            out += "\t" * (depth + 1)
            out += "\"args\": [\n"
            
            i = 0
            while i < len(ast.data[0]):
                out += "\t" * (depth + 2)
                out += "\"" + ast.data[0][i] + "\""
                if i + 1 < len(ast.data[0]):
                    out += ",\n"
                else:
                    out += "\n"
                i += 1
                
            out += "\t" * (depth + 1)
            out += "],\n"
            out += "\t" * (depth + 1)
            out += "\"statements\": [\n"
            out += printAst(ast.data[1], depth + 2)
            out += "\t" * (depth + 1)
            out += "]\n"
            out += "\t" * depth
            out += "}"
        elif ast.type == PARSER.VARASSIGN:
            out += "\t" * depth
            out += "\"varassign\": {\n"
            out += "\t" * (depth + 1)
            out += "\"location\": \"" + str(ast.loc) + "\",\n"
            out += "\t" * (depth + 1)
            out += "\"name\": " + printAst(ast.data[0], depth + 1) + ",\n"
            out += "\t" * (depth + 1)
            out += "\"operator\": \"" + str(ast.data[1]) + "\",\n"
            out += "\t" * (depth + 1)
            out += "\"value\": "
            
            if type(ast.data[2]) == token:
                out += "{\n"
                out += printAst(ast.data[2], depth + 2)
                out += "\n"
                out += "\t" * (depth + 1)
                out += "}"
            else:    
                out += printAst(ast.data[2], depth + 1)
            out += "\n"
            out += "\t" * depth
            out += "}"
        elif ast.type == PARSER.FUNCCALL:
            out += "\t" * depth
            out += "\"funccall\": {\n"
            out += "\t" * (depth + 1)
            out += "\"location\": \"" + str(ast.loc) + "\",\n"
            out += "\t" * (depth + 1)
            out += "\"name\": " + printAst(ast.data[0], depth + 1) + ",\n"
            out += "\t" * (depth + 1)
            out += "\"args\": [\n"
            
            i = 1
            while i < len(ast.data):
                out += "\t" * (depth + 2)
                if ast.data[i].type == PARSER.EXPR:
                    out += "{\n"
                    out += printAst(ast.data[i], depth + 3)
                    out += "\t" * (depth + 2)
                    out += "}"
                else:
                    out += printAst(ast.data[i], depth + 2)
                if i + 1 < len(ast.data):
                    out += ",\n"
                else:
                    out += "\n"
                i += 1
                
            out += "\t" * (depth + 1)
            out += "]\n"
            out += "\t" * depth
            out += "}"
             
                
        else:
            out += "\t" * depth
            out += "\"" + str(ast.type) + "\": { \n"
            out += "\t" * (depth + 1)
            out += "\"location\": \"" + str(ast.loc) + "\"\n"
            out += "\t" * depth
            out += "}"
            
            
    elif type(ast) is list:
        for i in ast:
            out += "\t" * depth
            out += "{\n"
            out += printAst(i, depth + 1)
            out += "\n"
            out += "\t" * depth
            out += "},\n"
            
        out = out[:-2]
        out += "\n"
            
    elif type(ast) is str:
        out += "\t" * depth
        out += "\"" + ast + "\""
        
    elif type(ast) is int:
        out += "\t" * depth
        out += str(ast)
            
    return out