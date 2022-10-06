#region basic

class location:
    def __init__(self, file: str, x: int, y: int) -> None:
        self.file = file
        self.x = x
        self.y = y
        
    def __repr__(self) -> str:
        return f"{self.file}:{self.x}:{self.y}"

class token:
    def __init__(self, loc: location) -> None:
        self.loc = loc
        
#endregion
                  
# region lexer token types:

class intl(token):
    def __init__(self, loc: location, data: int) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        return f"int({self.value})"
    
class floatl(token):
    def __init__(self, loc: location, data: float) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        return f"float({self.value})"
        
class charl(token):
    def __init__(self, loc: location, data: str) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        return f"char({self.value})"
        
class stringl(token):
    def __init__(self, loc: location, data: str) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        return f"string({self.value})"
      
class booll(token):
    def __init__(self, loc: location, data: bool) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        return f"bool({self.value})"
        
class id(token):
    def __init__(self, loc: location, data: str) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        return f"id({self.value})"

class op(token):
    def __init__(self, loc: location, data: str) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        return f"oper({self.value})"
    
class group(token):
    def __init__(self, loc: location, data: str) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        return f"group: {self.value}"
    
class comma(token):
    def __init__(self, loc: location) -> None:
        super().__init__(loc)
        
    def __str__(self) -> str:
        return f"comma"
    
class semi(token):
    def __init__(self, loc: location) -> None:
        super().__init__(loc)
        
    def __str__(self) -> str:
        return f"semi"
    
class filel(token):
    def __init__(self, loc: location) -> None:
        super().__init__(loc)
        
    def __str__(self) -> str:
        return f"file: {self.loc.file}"

class eof(token):
    def __init__(self, loc: location) -> None:
        super().__init__(loc)
        
    def __str__(self) -> str:
        return f"eof: {self.loc.file}"
    
#endregion
    
# region parser token types:

class unit(token):
    def __init__(self, loc: location, data: list[token]) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        out = "unit: {\n"
        out += f"location: {self.loc}\n"
        out += "body: [\n"
        out += "\t" + "\n\t".join([str(x) for x in self.value])
        out += " ]\n"
        out += "}"
        
        return out
    
class program(token):
    def __init__(self, loc: location, data: list[unit]) -> None:
        super().__init__(loc)
        self.value = data
        
    def __str__(self) -> str:
        out = "program: {\n"
        out += f" location: {self.loc}"
        out += " body: [\n"
        out += "\t" + "\n\t".join([str(x) for x in self.value])
        out += " ]\n"
        out += "}"
        
        return out
    
class expr(token):
    def __init__(self, loc: location, op: str, lhs: token, rhs: token = None) -> None:
        super().__init__(loc)
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        
    def __str__(self) -> str:
        out = "expr: {\n"
        out += f"op: {self.op}\n"
        out += f"lhs: {self.lhs}\n"
        out += f"rhs: {self.rhs}\n"
        out += "}"
        return out
    
class typep(token):
    def __init__(self, loc: location, typename: str, generics: list[token] = None, returns: list[token] = None) -> None:
        super().__init__(loc)
        self.typename = typename
        self.generics = generics
        self.returns = returns
        
        
    def __str__(self) -> str:
        out = "type: {\n"
        out += f"typename: {self.typename}\n"
        out += f"generics: ["
        if self.generics != None:
            out += "\n" + "\n".join([ str(x.typename) for x in self.generics]) + "\n"
            
        out += " ]\n"
        out += f"returns: ["
        if self.returns != None:
            out += "\n" + "\n".join([str(x.typename) for x in self.returns]) + "\n"
        out += " ]\n"
        out += "}"
        return out
    
class vardecl(token):
    def __init__(self, loc: location, name: str, type: typep, value: token = None) -> None:
        super().__init__(loc)
        self.name = name
        self.type = type
        self.value = value
        
    def __str__(self) -> str:
        out = "vardecl: {\n"
        out += f"location: {self.loc}\n"
        out += f"name: {self.name}\n"
        out += f"type: {self.type}\n"
        out += f"value: {self.value}\n"
        out += "}"
        return out

class funcdecl(token):
    def __init__(self, loc: location, args: list[id], body: list[token], defualts: list[expr] = None) -> None:
        super().__init__(loc)
        self.args = args
        self.body = body
        self.dafualts = defualts
        
    def __str__(self) -> str:
        out = "funcdecl: {\n"
        out += f"location: {self.loc}\n"
        out += f"args: ["
        if self.args:
            out += "\n\t" + "\n\t".join([str(x) for x in self.args]) + "\n"
        out += "]\n"
        out += f"defaults: ["
        if self.dafualts:
            out += "\n\t" + "\n\t".join([str(x) for x in self.dafualts]) + "\n"
        out += "]\n"
        out += f"body: [\n"
        out += "\t" + "\n\t".join([str(x) for x in self.body])
        out += "\n]\n"
        out += "}"
        return out
    
class structdecl(token):
    def __init__(self, loc: location, name: str, types: list[type]) -> None:
        super().__init__(loc)
        self.name = name
        self.types = types
        
    def __str__(self) -> str:
        out = "structdecl: {\n"
        out += f"location: {self.loc}\n"
        out += f"name: {self.name}\n"
        out += f"types: ["
        if self.types:
            out += "\n\t" + "\n\t".join([str(x) for x in self.types]) + "\n"
        out += "\n]\n"
        out += "}"
        return out
    
class classdecl(token):
    pass

class varassign(token):
    def __init__(self, loc: location, name: str, oper: str, value: token) -> None:
        super().__init__(loc)
        self.name = name
        self.oper = oper
        self.value = value
        
    def __str__(self) -> str:
        out = "varassign: {\n"
        out += f"location: {self.loc}\n"
        out += f"name: {self.name}\n"
        out += f"value: {self.oper}\n"
        out += f"value: {self.value}\n"
        out += "}"
        return out
    
class funccall(token):
    def __init__(self, loc: location, name: str, args: list[token]) -> None:
        super().__init__(loc)
        self.name = name
        self.args = args
        
    def __str__(self) -> str:
        out = "funccall: {\n"
        out += f"location: {self.loc}\n"
        out += f"name: {self.name}\n"
        out += f"args: ["
        if self.args:
            out += "\n\t" + "\n\t".join([str(x) for x in self.args]) + "\n"
        out += "]\n"
        out += "}"
        return out
    

class ifstate(token):
    def __init__(self, loc: location, cond: expr, body: list[token], ifelse: list[token] = None, elsebody: list[token] = None) -> None:
        super().__init__(loc)
        self.cond = cond
        self.body = body
        self.ifelse = ifelse
        self.elsebody = elsebody    
        
    def __str__(self) -> str:
        out = "ifstate: {\n"
        out += f"location: {self.loc}\n"
        out += f"cond: {self.cond}\n"
        out += f"body: ["
        if self.body:
            out += "\n\t" + "\n\t".join([str(x) for x in self.body]) + "\n"
        out += "]\n"
        out += f"ifelse: ["
        if self.ifelse:
            out += "\n\t" + "\n\t".join([str(x) for x in self.ifelse]) + "\n"
        out += "]\n"
        out += f"elsebody: ["
        if self.elsebody:
            out += "\n\t" + "\n\t".join([str(x) for x in self.elsebody]) + "\n"
        out += "]\n"
        out += "}"
        return out
    
class whilestate(token):
    def __init__(self, loc: location, cond: expr, body: list[token]) -> None:
        super().__init__(loc)
        self.cond = cond
        self.body = body
        
    def __str__(self) -> str:
        out = "whilestate: {\n"
        out += f"location: {self.loc}\n"
        out += f"cond: {self.cond}\n"
        out += f"body: ["
        if self.body:
            out += "\n\t" + "\n\t".join([str(x) for x in self.body]) + "\n"
        out += "]\n"
        out += "}"
        return out
    
class forstate(token):
    pass

class returnstate(token):
    def __init__(self, loc: location, value: token) -> None:
        super().__init__(loc)
        self.value = value
        
    def __str__(self) -> str:
        out = "returnstate: {\n"
        out += f"location: {self.loc}\n"
        out += f"value: {self.value}\n"
        out += "}"
        return out
    
class index(token):
    def __init__(self, loc: location, name: token, index: expr) -> None:
        super().__init__(loc)
        self.name
        self.index = intl

    def __str__(self) -> str:
        out = "index: {\n"
        out += f"name: {self.name}\n"
        out += f"index: {self.index}\n"
        out += "}"
        return out

class member(token):
    def __init__(self, loc: location, name: token, member: str) -> None:
        super().__init__(loc)
        self.name = name
        self.member = member
    
    def __str__(self) -> str:
        out = "member: {\n"
        out += f"name: {self.name}\n"
        out += f"member: {self.member}\n"
        out += "}"
        return out
    
# endregion
   
def allign(text: any, width: int) -> str:
    """ returns a string with 'width' spaces after 'text'

    Args:
        text (any): text to allign, will be converted to string
        width (int): width of the alligned text

    Returns:
        str: alligned text
    """
    return str(text) + " " * (width - (len(str(text))))
    
def error(msg: str):
    """ prints an error message and exits

    Args:
        msg (str): message to print
    """
    print("[\u001b[31;1m", end="")
    print("ERROR", end="")
    print("\u001b[0m]: ", end="")
    print(msg)
    print("[INFO]: exiting...")
    exit(0)
    
def todo(func: str, msg: str):
    """ prints a todo message and exits

    Args:
        func (str): function to work on
        msg (str):  message to print
    """
    print("[\u001b[33;1m", end="")
    print("TODO", end="")
    print("\u001b[0m]: ", end="")
    print(f"implement \'{msg}\' at {func}")
    print("[INFO]: exiting...")
    exit(0)
    
def warn(msg: str):
    """ prints a warning message

    Args:
        msg (str): message to print
    """
    print("[\u001b[33;1m", end="")
    print("WARN", end="")
    print("\u001b[0m]: ", end="")
    print(msg)
    
def info(msg: str):
    """ prints an info message

    Args:
        msg (str): message to print
    """
    print("[INFO]: ", end="")
    print(msg)
         
def usage():
    """ prints the usage of the program and exits
    """
    
    print("Usage: scribe [options] file")
    print("options:")
    print("\t -c                    compile file")
    print("\t -r                    run file after compiling")
    print("\t -i                    run and remove file after compiling")
    print("\t -o outfile            output redirection (default=$file)")
    print("\t -vl,--verbose_lex     verbose lexer output")
    print("\t -vx,--verbose_com     verbose compiler output")
    print("\t -h,--help             prints this screen")
    print("\t -S outfile            Write asm to file and keep asm")
    exit(0)