from pysrc.compiler import *
from pysrc.tools import *

from os import system
import tempfile


def generate64(tokarr: list[compiler_token], filename: str, keep: str):
    
    # check is fasm is installed
    if system("fasm -h 1> /dev/null 2>/dev/null") != 256:
        error("jscribe compiler needs fasm installed to generate executables\n" + 
              "[INFO]: use `sudo apt install fasm` or your local package manager to install fasm")
        
    asmname = 0
        
    if len(keep) == 0:
        asmname = next(tempfile._get_candidate_names())
    else:
        asmname = keep
        
    with open(asmname, "w") as asmfile:
        
        asmfile.write("format ELF64 executable\n")
        asmfile.write("entry start\n")
        asmfile.write("segment readable executable\n")
        asmfile.write("\n")
        asmfile.write("start:\n")
        
        ret = writeasm64(tokarr, asmfile, 0)
        
        asmfile.write("    mov rax, 60 ; SYSEXIT\n")
        asmfile.write("    mov rdi, 0\n")
        asmfile.write("    syscall\n")
        asmfile.write("\n")
        
        if len(ret) != 0:
            asmfile.write("segment readable writable\n")
            for string in ret:
                asmfile.write(string)
         
    print(f"[CMD]: fasm {asmname} {filename}")
    if system(f"fasm {asmname} {filename} 1> /dev/null") != 0:
        error("fasm ran into an error")
    print(f"[CMD]: chmod +x {filename}")
    system(f"chmod +x {filename}")
    
    if len(keep) == 0:
        print(f"[CMD]: rm {asmname}")
        system(f"rm {asmname}")
    elif keep == "stdout":
        print("")
        system(f"cat {asmname}")
        print(f"[CMD]: rm {asmname}")
        system(f"rm {asmname}")
        
    

def writeasm64(tokarr: list[compiler_token], file: TextIOWrapper, count: int):
    
    # check is fasm is installed
    if system("fasm -h 1> /dev/null 2>/dev/null") != 256:
        error("jscribe compiler needs fasm installed to generate executables\n" + 
              "[INFO]: use `sudo apt install fasm` or your local package manager to install fasm")
    
    datarr = []
    asmname = 0

    for token in tokarr:
            
        match token.context:
            case CTX.DEBUG:
                
                match token.data.type:
                    
                    case CTX_DEBUG.STR:
                        file.write(f"    mov rax, 1 ; SYS_WRITE\n")
                        file.write(f"    mov rdi, 1 ; STDOUT\n")
                        file.write(f"    mov rsi, l{count}.str\n")
                        file.write(f"    mov rdx, l{count}.len\n")
                        file.write(f"    syscall\n")
                        file.write("\n")
                        
                        datarr.append(f"    l{count}.str db {token.data.value}, 10\n")
                        datarr.append(f"    l{count}.len = $- l{count}.str\n")
                        datarr.append("\n")
                        count += 1
                    
                    case CTX_DEBUG.INT:
                        datarr += writeasm64(token.data.value, file, count + 3)
                        file.write("\n")
                        
                        file.write(f"    mov rbx, 10\n")
                        file.write(f"    mov rcx, 0\n")
                        file.write(f"l{count}:\n")
                        file.write(f"    mov rdx, 0\n")
                        file.write(f"    idiv rbx\n")
                        file.write(f"    push rdx\n")
                        file.write(f"    inc rcx\n")
                        file.write(f"    cmp rax, 9\n")
                        file.write(f"    jg l{count}\n")
                        file.write(f"    mov r10, rcx\n")
                        file.write(f"    add r10, 2\n")
                        file.write(f"    push rax\n")
                        file.write(f"    mov rax, 0\n")
                        file.write(f"l{count + 1}:\n")
                        file.write(f"    pop rdx\n")
                        file.write(f"    add rdx, '0'\n")
                        file.write(f"    mov [l{count+2}.str + rax], dl\n")
                        file.write(f"    dec rcx\n")
                        file.write(f"    inc rax\n")
                        file.write(f"    cmp rcx, 0\n")
                        file.write(f"    jge l{count+1}\n")
                        file.write(f"    mov [l{count+2}.str + rax], 10\n")
                        file.write(f"\n")
                        file.write(f"    mov rax, 1 ; SYS_WRITE\n")
                        file.write(f"    mov rdi, 1 ; STDOUT\n")
                        file.write(f"    mov rsi, l{count + 2}.str\n")
                        file.write(f"    mov rdx, r10\n")
                        file.write(f"    syscall\n")
                        file.write(f"\n")
                        count += 2
                        
                        datarr.append(f"    l{count}.str rb 16")
                        datarr.append("\n")
                        count += 1
                    
                    case _:
                        system(f"rm {asmname}")
                        ptodo(f"generation of debug token \'{CTX_DEBUG.STRING[token.data.type]}\'")
                
            case CTX.LOAD:
                file.write(f"    mov rax, {token.data}\n")
                
            case CTX.ADD:
                file.write(f"    add rax, {token.data}\n")
                
            case CTX.MUL:
                file.write(f"    mov rdx, 0\n")
                file.write(f"    mov rbx, {token.data}\n")
                file.write(f"    imul rbx\n")
                
            case CTX.DIV:
                file.write(f"    mov rdx, 0\n")
                file.write(f"    mov rbx, {token.data}\n")
                file.write(f"    idiv rbx ")
                
            case CTX.MOD:
                file.write(f"    mov rdx, 0\n")
                file.write(f"    mov rbx, {token.data}\n")
                file.write(f"    idiv rbx\n")
                file.write(f"    mov rax, rdx\n")
                
            case CTX.SUB:
                file.write(f"    sub rax, {token.data}\n")
                
            case _:
                system(f"rm {asmname}")
                ptodo(f"generation of token \'{CTX.STRING[token.context]}\'")

    return datarr
    