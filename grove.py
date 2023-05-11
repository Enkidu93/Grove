# The interpreter we wrote is a dynamic type of system because we use a dictionary with string keys. 
# The value in the dictionary is the reference of the variable, so the key can point to an instance 
# of a integer on one line, then on the next it can point to a string. This effectively makes our 
# interpreter dynamic.

from grove_lang_lang import *

def main():
    # print("Welcome to the Grove Interpreter!")
    while True:
        s: str = input('Grove>> ')
        try:
            x = Command.parse(s).eval()
            if x is not None: print(x)
        except GroveParseError as e:
            print(f"Error Parsing {s}")
            print(e)
        except GroveEvalError as e:
            print(f"Error Evaluating {s}")
            print(e)

if __name__ == "__main__":
	main()