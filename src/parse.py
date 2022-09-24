from ast import arg
from cmath import exp
from re import L
from src.common import *
    
tok: token = None
    
def parse64(ltokens: list[token], verbose: bool):    
    
    ltokens.reverse()
    out: list[token] = []
    
    def next():
        global tok
        if len(ltokens) > 0:
            tok = ltokens.pop()
        else:
            tok = None        
    def peek(loc: int) -> token:
        if len(ltokens) >= loc:
            return ltokens[-loc]
        else: 
            return None 
    def accept(type: Enum, data: any = None) -> bool:
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
        if tok.type == type:
            if data is None:
                return True
            elif tok.data == data:
                return True
        return False
    def expect(type: Enum, data: any = None) -> bool:
        global tok 
        if accept(type, data):
            return True
        if data is None:
            error(f"{tok.loc}: expected {type}, got {tok.type} instead.")
        else:
            error(f"{tok.loc}: expected {type} {data}, got {tok.type} {tok.data} instead.")
    
    def makeUnit() -> token:
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
        temp = token(tok.loc, PARSER.VARDECL, [makeType()])
        temp.data.append(tok)
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
        
    def makeFuncDecl() -> token:
        
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
                error(f"{tok.loc}: function definition expects closing brace, none found.")
                
            datlist.append(makeStatement())
            
        temp.data.append(arglist)
        temp.data.append(datlist)
        
        return temp
    
    def makeStatement() -> token:
        
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
            
            if peek(1) == LEXER.ID:
                return makeVarDecl()
            elif peek(1) == LEXER.OP and peek(1).data == "<":
                return makeVarDecl()
            else:
                temp = makeExpr()
                expect(LEXER.SEMI)
                return temp
        else:
            temp = makeExpr()
            expect(LEXER.SEMI)
            return temp
    
    def makeClassDecl() -> token:
        todo("parse64", "makeClassDecl")
        return
    def makePreProc() -> token:
        
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
        
    def makeType() -> token:
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
        if accept(LEXER.ID, "true"):
            return token(tok.loc, PARSER.BOOL, "true")
        elif accept(LEXER.ID, "false"):
            return token(tok.loc, PARSER.BOOL, "false")
        elif check(LEXER.ID) and peek(1).type == LEXER.GROUP and peek(1).data == "(":
            return makeFuncCall()
        else:
            temp = makeLogic()
            return temp
    
    def makeFuncCall() -> token:
        todo("parse64", "makeFuncCall")
        
    def makeIfState() -> token:
        temp = token(tok.loc, PARSER.IF, [])
        
        datlist = []
        eliflist = []
        elselist = []
        
        expect(LEXER.GROUP, "(")
        temp.data.append(makeConditional())
        expect(LEXER.GROUP, ")")
        
        if accept(LEXER.GROUP, "{"):
            while not accept(LEXER.GROUP, "}"):
                if accept(LEXER.EOF):
                    error(f"{tok.loc}: if statement expects closing brace, none found.")
                datlist.append(makeStatement())
        else:
            datlist.append(makeStatement())
        
        while accept(LEXER.ID, "else"):
            
            if accept(LEXER.ID, "if"):
                
                temp1 = token(tok.loc, PARSER.IF, [])
                datlist1 = []
                
                expect(LEXER.GROUP, "(")
                temp1.data.append(makeConditional())
                expect(LEXER.GROUP, ")")
                
                if accept(LEXER.GROUP, "{"):
                    while not accept(LEXER.GROUP, "}"):
                        if accept(LEXER.EOF):
                            error(f"{tok.loc}: if statement expects closing brace, none found.")
                        datlist1.append(makeStatement())
                else:
                    datlist1.append(makeStatement())
                
                temp1.data.append(datlist1)
                eliflist.append(temp1)
                
            else:
                if accept(LEXER.GROUP, "{"):
                    while not accept(LEXER.GROUP, "}"):
                        if accept(LEXER.EOF):
                            error(f"{tok.loc}: else statement expects closing brace, none found.")
                        elselist.append(makeStatement())
                else:
                    elselist.append(makeStatement())  
        
        temp.data.append(datlist)
        if elselist != []:
            temp.data.append(eliflist)
            temp.data.append(elselist)
        elif eliflist != []:
            temp.data.append(eliflist)
        
        return temp
        
        todo("parse64", "makeIf")
        
    def makeWhileState() -> token:
        todo("parse64", "makeWhile")
        
    def makeForState() -> token:
        todo("parse64", "makeFor")
        
    def makeReturn() -> token:
        temp = token(tok.loc, PARSER.RETURN, None)
        if accept(LEXER.SEMI):
            return temp
        temp.data = makeExpr()
        expect(LEXER.SEMI)
        return temp
        
    def makeConditional() -> token:
        
        temp = token(tok.loc, PARSER.CONDITION, [makeExpr()])
        
        if accept(LEXER.OP, "=="):
            temp.data.append(makeExpr())
            temp.data.append("==")
        elif accept(LEXER.OP, "!="):
            temp.data.append(makeExpr())
            temp.data.append("!=")
        elif accept(LEXER.OP, ">"):
            temp.data.append(makeExpr())
            temp.data.append(">")
        elif accept(LEXER.OP, ">="):
            temp.data.append(makeExpr())
            temp.data.append(">=")
        elif accept(LEXER.OP, "<"):
            temp.data.append(makeExpr())
            temp.data.append("<")
        elif accept(LEXER.OP, "<="):
            temp.data.append(makeExpr())
            temp.data.append("<=")
        elif accept(LEXER.OP, "&&"):
            temp.data.append(makeExpr())
            temp.data.append("&&")
        elif accept(LEXER.OP, "||"):
            temp.data.append(makeExpr())
            temp.data.append("||")
        elif accept(LEXER.OP, "^^"):
            temp.data.append(makeExpr())
            temp.data.append("^^")
        
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
            return temp
        else:
            error(f"{tok.loc}: expected value, got {tok.type} instead.")
            
    next()
    out = makeUnit()
    print(out)
    return out


