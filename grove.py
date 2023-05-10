# from grove_parse import *
from grove_lang_lang import *

def main():
    # print("Welcome to the Grove Interpreter!")
    while True:
        s: str = input('Grove>> ')
        try:
            x = Command.parse(s).eval()
            if x is not None: print(x)
        except GroveLangParseException as e:
            print(f"Error Parsing {s}")
            print(e)
        except GroveLangEvalException as e:
            print(f"Error Evaluating {s}")
            print(e)

if __name__ == "__main__":
	main()