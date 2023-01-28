from src.common import *

def generate64(il: list[token], outfile: str, verbose: bool):
    
    with open(outfile, "w") as file:
        for tok in il:
            if isinstance(tok, il_label):
                file.write(f"{tok.name}:\n")
            elif isinstance(tok, il_mov):
                file.write(f"mov {tok.target}, {tok.value}\n")
            elif isinstance(tok, il_push):
                file.write(f"push {tok.value}\n")
            elif isinstance(tok, il_pop):
                file.write(f"pop {tok.target}\n")
            elif isinstance(tok, il_call):
                file.write(f"call {tok.target}\n")
            elif isinstance(tok, il_return):
                file.write(f"ret\n")
            elif isinstance(tok, il_exit):
                file.write(f"exit\n")
            else:
                todo("generate64", f"{type(tok).__name__}")
    
    pass