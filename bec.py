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
                print(f"[INFO]: lexer finished in {(time.time_ns() - curtime) / 1000}ms")
                
            ptodo("compiling")
        
        elif args[0] == "-r":
            args = args[1:]
            run = True
        
        elif args[0] == "-v":
            args = args[1:]
            verbose = True
        
        elif args[0] == "-o":
            args = args[1:]
            
            if len(args) == 0:
                error("-o expects an output file, got nothing instead.")
            if args[0] in ("-c", "-i", "-v", "-o", "-h", "--help"):
                error(f"-o expects an output file, got \'{args[0]}\' instead.")
            
            outputfile = args[0]
            args = args[1:] 
        
        else:
            error(f"bec expected a command, got \'{args[0]}\' instead.")
    
    error(f"bec expected a command, got nothing instead.")

if __name__ == "__main__":
    main()