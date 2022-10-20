from io import TextIOWrapper
from src.common import *
import os as os

def lex64(file: TextIOWrapper, verbose: bool) -> list[token]:
    """ lexes a file and returns a list of tokens

    TODO: fix comments and location tracking, currently comments will sometimes not change the location over multiple lines
    TODO: determine if the lexer should be able to handle multiple files, and if it should handle includes

    Args:
        file (TextIOWrapper): file to lex, must be opened in read mode
        verbose (bool): verbose output

    Returns:
        list[token]: list of lexer tokens
    """
    
    filename = file.name
    text = file.read() + "\n"
    
    tokens = [filel(location(filename, 0, 0))]
    
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
                line += 1
                depth = 0
            
        
        ## SPACE ##
                
        if char in " \t\n":
            if char == "\n":
                line += 1
                depth = 0
            
        
        ## SEPARATORS ##
        
        elif char == ";":
            tokens.append(semi(location(filename, line, depth)))
        elif char == ",":
            tokens.append(comma(location(filename, line, depth)))
        elif char in "()[]{}":
            tokens.append(group(location(filename, line, depth), char))
            
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
                tokens.append(floatl(location(filename, line, cdepth), float(num)))
            else:
                tokens.append(intl(location(filename, line, cdepth), int(num)))
        
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
            
            if name == "true" or name == "false":
                tokens.append(booll(location(filename, line, cdepth), name))
            else:
                tokens.append(id(location(filename, line, cdepth), name))
            
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
            
            tokens.append(charl(location(filename, line, cdepth), name))
            
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
            
            tokens.append(stringl(location(filename, line, cdepth), name))
            
        ## OPERATORS ##
            
        elif char in "+-*/%=<>!&|^~.?":
            if char == text[pos + 1] and char in "+-=&|^":
                tokens.append(op(location(filename, line, depth), char + char))
                pos += 1
            elif text[pos + 1] == "=" and char not in ".~":
                tokens.append(op(location(filename, line, depth), char + "="))
                pos += 1
            elif char == "-" and text[pos + 1] == ">":
                tokens.append(op(location(filename, line, depth), "->"))
                pos += 1
            else:
                tokens.append(op(location(filename, line, depth), char))
            
        ## ERROR ##
            
        else:
            error(f"{location(filename, line, depth)}: unexpected character {char} found")
                
        ## END OF LOOP ##
            
        depth += 1
        pos += 1
    
    
    tokens.append(eof(location(filename, line, 0)))
    
    if verbose:
        
        longest = 0
        [longest := max(longest, len(str(token))) for token in tokens]
        
        out = "\n".join([allign(str(x.loc) + ": ", longest + 3) + str(x) for x in tokens])
        
        if not os.path.exists(".out"):
            os.mkdir(".out")
            print(" -> [LEXER]: created .out directory")
            
        if not os.path.exists(".out/lexer"):
            os.mkdir(".out/lexer")
            print(" -> [LEXER]: created .out/lexer directory")
            
        with open(".out/lexer/" + tokens[0].loc.file.split("/")[-1], "w") as file:
            file.write(out)
        
        print(" -> [LEXER]: wrote tokens to .out/lexer/" + tokens[0].loc.file.split("/")[-1])

        
    return tokens
