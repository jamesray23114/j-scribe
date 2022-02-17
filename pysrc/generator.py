from pysrc.compiler import *
from pysrc.tools import *

from os import system
import tempfile


def generate64(tokarr: list[compiler_token], filename: str, keep: str):
    
    # check is fasm is installed
    if system("fasm -h 1> /dev/null 2>/dev/null") != 256:
        error("jscribe compiler needs fasm installed to generate executables\n" + 
              "[INFO]: use `sudo apt install fasm` or your local package manager to install fasm")
    
    datarr = []
    count = 0
    asmname = 0
    if len(keep) == 0:
        asmname = next(tempfile._get_candidate_names()) + ".asm"
    else:
        asmname = keep
    
    with open(asmname, "w") as asm:
        asm.write("format ELF64 executable\n")
        asm.write("entry start\n")
        asm.write("segment readable executable\n")
        asm.write("\n")
        asm.write("start:\n")
    
        for token in tokarr:
            
            match token.context:
                case CTX.DEBUG:
                    
                    match token.data.type:
                        
                        case LEX.STR:
                            asm.write(f"    mov rax, 1 ; SYS_WRITE\n")
                            asm.write(f"    mov rdi, 1 ; STDOUT\n")
                            asm.write(f"    mov rsi, l{count}.str\n")
                            asm.write(f"    mov rdx, l{count}.len\n")
                            asm.write(f"    syscall\n")
                            asm.write("\n")
                            
                            datarr.append(f"    l{count}.str db {token.data.data}, 10\n")
                            datarr.append(f"    l{count}.len = $- l{count}.str\n")
                            datarr.append("\n")
                            count += 1
                        
                        case LEX.INT | LEX.CHAR | LEX.FLT:
                            asm.write(f"    mov rax, 1 ; SYS_WRITE\n")
                            asm.write(f"    mov rdi, 1 ; STDOUT\n")
                            asm.write(f"    mov rsi, l{count}.str\n")
                            asm.write(f"    mov rdx, l{count}.len\n")
                            asm.write(f"    syscall\n")
                            asm.write("\n")
                        
                            datarr.append(f"    l{count}.str db \"{str(token.data.data)}\", 10\n")
                            datarr.append(f"    l{count}.len = $- l{count}.str\n")
                            datarr.append("\n")
                            count += 1
                        
                        case _:
                            ptodo(f"generation of debug token \'{LEX.STRING[token.data.type]}\'")
                    
                case _:
                    ptodo(f"generation of token \'{CTX.STRING[token.context]}\'")
    
        asm.write("    mov rax, 60 ; SYSEXIT\n")
        asm.write("    mov rdi, 0\n")
        asm.write("    syscall\n")
        asm.write("\n")
    

        if len(datarr) != 0:
            asm.write("segment readable writable\n")
            for string in datarr:
                asm.write(string)
    
    print(f"[CMD]: fasm {asmname} {filename}")
    system(f"fasm {asmname} {filename} 1> /dev/null")
    
    if len(keep) == 0:
        print(f"[CMD]: rm {asmname}")
        system(f"rm {asmname}")
    