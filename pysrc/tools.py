from re import X
from sys import exit


class loc:
    def __init__(self, file: str, x: int, y: int) -> None:
        self.file = file
        self.x = x
        self.y = y
        pass
    
    def __repr__(self) -> str:
        return f"{self.file}:{self.x}:{self.y}"
    
def iota(reset=False):
    if reset:
        iota.val = 0
    else:
        iota.val += 1
    return iota.val
iota.val = 0

def usage():
    print("Usage: scribe [options] file")
    print("options:")
    print("\t -c                    compile file")
    print("\t -r                    run file after compiling")
    print("\t -i                    run and remove file after compiling")
    print("\t -o outfile            output redirection (default=$file)")
    print("\t -vl,--verbose_lex     verbose lexer output")
    print("\t -vx,--verbose_com     verbose compiler output")
    print("\t -h,--help             prints this screen")
    print("\t -S outfile            Write asm to file and keep asm (default="" dont keep file)")    
    exit(0)
    
def error(msg: str):
    print("[\u001b[31;1m", end="")
    print("ERROR", end="")
    print("\u001b[0m]: ", end="")
    print(msg)
    print("[INFO]: exiting...")
    exit(0)
    
def ptodo(msg: str):
    print("[\u001b[33;1m", end="")
    print("TODO", end="")
    print("\u001b[0m]: ", end="")
    print("implement " + msg)
    print("[INFO]: exiting...")
    exit(0)
    
def warn(msg: str):
    print("[\u001b[33;1m", end="")
    print("WARN", end="")
    print("\u001b[0m]: ", end="")
    print(msg)
    
    
def debug(stype: str, msg: any):
    print("-> [PRAGMA]: ", end="")
    print("(" + stype + ") " + str(msg))
    