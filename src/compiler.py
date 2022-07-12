from src.common import *


def expr(ltokens: list[token]) -> list[token]:
    ltokens.reverse()
    outtokens: list[token] = []
    
    while len(ltokens):
        tok = ltokens.pop()
        outtokens.append(tok)
        
    print(outtokens)
    return outtokens
            
def compile64(ltokens: list[token], verbose: bool):
    ltokens.reverse()

    outtokens: list[token] = []
    expr: list[token] = []
    
    while len(ltokens):
        tok = ltokens.pop()
        if tok.type == LEXER.FILE:
            pass
        elif tok.type == LEXER.EOF:
            pass
        elif tok.type == LEXER.SEMI:
            outtokens += expr(expr)
        else:
            expr.append(tok)

    
    
    todo("compile64", "compilation")
    
    return out