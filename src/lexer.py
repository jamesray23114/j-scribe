from io import TextIOWrapper
from src.common import *

def lex64(file: TextIOWrapper, verbose: bool) -> list[token]:
    
    filename = file.name
    text = file.read() + "\n"
    
    tokens = [token(location(filename, 0, 0), LEXER.FILE, filename)]
    
    line = 1
    depth = 1
    pos = 0
    
    while pos < len(text):
        char = text[pos]

        ## REMOVE COMMENTS ##

        if char == "/":
            if text[pos + 1] == "/":
                while char != "\n":
                    pos += 1
                    char = text[pos]
                if tokens[len(tokens) - 1].type != LEXER.SPACE:
                    tokens.append(token(location(filename, line, depth), LEXER.SPACE, None))
                
        ## SPACE ##
                
        elif char in " \t\n":
            if char == "\n":
                line += 1
                depth = 0
        
        ## SEPARATORS ##
        
        elif char == ";":
            tokens.append(token(location(filename, line, depth), LEXER.SEMI, ";"))
        elif char == ",":
            tokens.append(token(location(filename, line, depth), LEXER.COMMA, ","))
            
        ## INTEGERS AND FLOATS ##
            
        elif char in "0123456789": 
            num = ""
            cdepth = depth
            isFloat = False
            
            while char.isnumeric() or (char == "." and not isFloat):
                if char == ".":
                    isFloat = True
                num += char
                depth += 1
                pos += 1
                char = text[pos]
            pos -= 1
            depth -= 1
            
            if isFloat:
                tokens.append(token(location(filename, line, cdepth), LEXER.FLOAT, float(num)))
            else:
                tokens.append(token(location(filename, line, cdepth), LEXER.INT, int(num)))
        
        ## NAMES ##
        
        elif char.isalpha(): # names
            name = ""
            cdepth = depth
            
            while char.isalnum() or char in "-?_":
                name += char
                depth += 1
                pos += 1
                char = text[pos]
            
            pos -= 1
            depth -= 1
            
            tokens.append(token(location(filename, line, cdepth), LEXER.WORD, name))
            
        ## CHARACTERS ##  
            
        elif char == "\'": 
            name = ""
            cdepth = depth
            started = False
            
            while char != "\'" or not started:
                started = True
                if char == "\n":
                    error(f"{location(filename, line, cdepth)}: opening quote expects closing quote but got none instead")
                if char != "\'":
                    name += char
                depth += 1
                pos += 1
                char = text[pos]
            
            tokens.append(token(location(filename, line, cdepth), LEXER.CHAR, name))
            
        ## STRINGS ##
            
        elif char == "\"": 
            name = ""
            cdepth = depth
            started = False
            
            while char != "\"" or not started:
                started = True
                if char == "\n":
                    error(f"{location(filename, line, cdepth)}: opening quote expects closing quote but got none instead")
                if char != "\"":
                    name += char
                depth += 1
                pos += 1
                char = text[pos]
            
            tokens.append(token(location(filename, line, cdepth), LEXER.STRING, name))
            
        ## OPERATORS ##
            
        elif char in "!$#%^&*-=+@|/?<>[]:.(){}": 
            tokens.append(token(location(filename, line, depth), LEXER.SYMB, char))
            
        ## ERROR ##
            
        else:
            error(f"{location(filename, line, depth)}: unexpected character {char} found")
                
        ## END OF LOOP ##
            
        depth += 1
        pos += 1
    
    
    tokens.append(token(location(filename, line, 0), LEXER.EOF, filename))
    
    if verbose:
        printTokArray(tokens, " -> [LEXER]: ")
        
    return tokens

    