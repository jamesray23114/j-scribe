from src.common import *

def parse64(ltokens: list[token], verbose: bool):
    ltokens.reverse()
    out: list[token] = []
    pstack: list[token] = []
    curfile = 0
    
    pstack.append(ltokens.pop())
    while (len(ltokens) > 0) or (len(pstack) > 0):
        tok = pstack[-1]
        
        if tok.type == LEXER.FILE:
            pstack.pop()
            pstack.append(token(tok.loc, PARSER.UNIT, None))
        
        elif tok.type == LEXER.EOF:
            tok = pstack[0]
            tok.data = pstack[1:-1]
            out.append(tok)
            pstack = []
            
        elif tok.type == LEXER.ID:
            pstack.pop()
            pstack.append(token(tok.loc, PARSER.VALUE, tok.data))
            
        else:
            pstack.append(ltokens.pop())
    
        input()
        if verbose:
            printTokArray(pstack, "pstack: ")
            printTokArray(out, " -> [PARSE]: ")
    
    todo("parse64", "parsing")
    return out


