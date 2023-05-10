# identify the current directory of this script and add it to the path
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# import all node types from the calc language
from calc_lang import *

def main():
    print("Welcome to the Calc Interpreter!")
    print("Enter your commands or ':done' to exit")
    # loop until the command :done is found
    while True:
        s: str = input('> ')
        if s.strip() == ':done': break
        try:
            x = Command.parse(s).eval()
            if x is not None: print(x)
        except CalcParseException as e:
            print(f"Error Parsing {s}")
            print(e)
        except CalcEvalException as e:
            print(f"Error Evaluating {s}")
            print(e)
    print("Goodbye and thank you for using Calc!")

if __name__=='__main__': main()