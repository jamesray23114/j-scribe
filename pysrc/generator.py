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
                        
                        case CTX_DEBUG.STR:
                            asm.write(f"    mov rax, 1 ; SYS_WRITE\n")
                            asm.write(f"    mov rdi, 1 ; STDOUT\n")
                            asm.write(f"    mov rsi, l{count}.str\n")
                            asm.write(f"    mov rdx, l{count}.len\n")
                            asm.write(f"    syscall\n")
                            asm.write("\n")
                            
                            datarr.append(f"    l{count}.str db {token.data.value}, 10\n")
                            datarr.append(f"    l{count}.len = $- l{count}.str\n")
                            datarr.append("\n")
                            count += 1
                        
                        case CTX_DEBUG.INT:
                            asm.write(f"    mov rbx, 10\n")
                            asm.write(f"    mov rcx, 0\n")
                            asm.write(f"l{count}:\n")
                            asm.write(f"    mov rdx, 0\n")
                            asm.write(f"    idiv rbx\n")
                            asm.write(f"    push rdx\n")
                            asm.write(f"    inc rcx\n")
                            asm.write(f"    cmp rax, 9\n")
                            asm.write(f"    jg l{count}\n")
                            asm.write(f"    push rax\n")
                            asm.write(f"    mov rax, 0\n")
                            asm.write(f"l{count + 1}:\n")
                            asm.write(f"    pop rdx\n")
                            asm.write(f"    add rdx, '0'\n")
                            asm.write(f"    mov [l{count+2}.str + rax], dl\n")
                            asm.write(f"    dec rcx\n")
                            asm.write(f"    inc rax\n")
                            asm.write(f"    cmp rcx, 0\n")
                            asm.write(f"    jge l{count+1}\n")
                            asm.write(f"    mov [l{count+2}.str + rax], 10\n")
                            asm.write(f"\n")
                            asm.write(f"    mov rax, 1 ; SYS_WRITE\n")
                            asm.write(f"    mov rdi, 1 ; STDOUT\n")
                            asm.write(f"    mov rsi, l{count + 2}.str\n")
                            asm.write(f"    mov rdx, 16\n")
                            asm.write(f"    syscall\n")
                            asm.write(f"\n")
                            count += 2
                            
                            datarr.append(f"    l{count}.str db 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0")
                            datarr.append("\n")
                            count += 1
                        
                        case _:
                            system(f"rm {asmname}")
                            ptodo(f"generation of debug token \'{CTX_DEBUG.STRING[token.data.type]}\'")
                    
                case CTX.LOAD:
                    asm.write(f"    mov eax, {token.data}\n")
                    
                case CTX.ADD:
                    asm.write(f"    add eax, {token.data}\n")
                    
                case CTX.SUB:
                    asm.write(f"    sub eax, {token.data}\n")
                    
                case _:
                    system(f"rm {asmname}")
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
    