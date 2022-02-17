from os import system
import pysrc.compiler as com, pysrc.generator as gen, pysrc.lexer as lex
from pysrc.tools import *
from sys import argv
from os.path import exists 
import time

def main():
    args = argv
    if len(args) == 1:
        usage()

    args = args[1:]
    
    outputfile = 0
    verbose = False
    run = False
    irun = False
    asmfile = ""
    
    while len(args):
        if args[0] == "-h" or args[0] == "--help": 
            usage()
            
        elif args[0] == "-c":
            args = args[1:]
            
            if len(args) == 0:
                error("-c expects an input file, got nothing instead.")
            if not exists(args[0]):
                error(f"invalid file, -c expects an input file, got \'{args[0]}\' instead.")
            
            ltokarr: list[lex.lexer_token] = []
            
            with open(args[0], "r") as file:
                curtime = time.time_ns()
                print("[INFO]: starting lexer")
                ltokarr = lex.lex64(file, verbose)
                print(f"[INFO]: lexer finished in {(time.time_ns() - curtime) / 1000000000:.8f} seconds")
            
            curtime = time.time_ns()
            print("[INFO]: starting compiler")    
            ctokarr: list[com.compiler_token] = com.compile64_to_oparray(ltokarr, verbose)
            print(f"[INFO]: compiler finished in {(time.time_ns() - curtime) / 1000000000:.8f} seconds")
            
            if outputfile == 0:
                outputfile = args[0].split("/")[-1].split(".")[0] + ".out"
            
            curtime = time.time_ns()
            print(f"[INFO]: starting generation")
            gen.generate64(ctokarr, outputfile, asmfile)
            print(f"[INFO]: generation finished in {(time.time_ns() - curtime) / 1000000000:.8f} seconds")

            if run:
                curtime = time.time_ns()
                print(f"[CMD]: ./{outputfile}\n")
                ex = system(f"./{outputfile}")
                print(f"\n[INFO]: file ran in {(time.time_ns() - curtime) / 1000000000:.8f} seconds and exited with exit code {ex}")
            elif irun:
                curtime = time.time_ns()
                print(f"[CMD]: ./{outputfile}\n")
                ex = system(f"./{outputfile}")
                print(f"\n[INFO]: file ran in {(time.time_ns() - curtime) / 1000000000:.8f} seconds and exited with exit code {ex}")
                print(f"[CMD]: rm {outputfile}")
                system(f"rm {outputfile}")                
            
            
            exit(0)
        
        elif args[0] == "-r":
            args = args[1:]
            run = True
            
        elif args[0] == "-i":
            args = args[1:]
            irun = True
        
        elif args[0] == "-v":
            args = args[1:]
            verbose = True
        
        elif args[0] == "-o":
            args = args[1:]
            
            if len(args) == 0:
                error("-o expects an output file, got nothing instead.")
            if args[0] in ("-c", "-i", "-v", "-o", "-h", "--help", "-s"):
                error(f"-o expects an output file, got \'{args[0]}\' instead.")
            
            outputfile = args[0]
            args = args[1:] 
        
        elif args[0] == "-S":
            args = args[1:]
            
            if len(args) == 0:
                error("-S expects and output file, got nothing instead.")
            if args[0] in ("-c", "-i", "-v", "-o", "-h", "--help", "-s"):
                error(f"-S expects an output file, got \'{args[0]}\' instead.")
            
            asmfile = args[0]
            args = args[1:]
        
        else:
            error(f"bec expected a command, got \'{args[0]}\' instead.")
    
    error(f"bec expected a command, got nothing instead.")

if __name__ == "__main__":
    main()