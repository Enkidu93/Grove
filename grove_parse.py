from grove_lang import *

# NOTE: if you use integrated parsing like we did for calc you can delete this file

# Utility methods for handling parse errors
def check(condition, message = "Unexpected end of expression"):
    """ Checks if condition is true, raising a ValueError otherwise """
    if not condition:
        raise GroveError("GROVE: " + message)
        
def expect(token, expected):
    """ Checks that token matches expected
        If not, throws a ValueError with explanatory message
    """
    check(token == expected, "Expected '" + expected + "' but found '" + token + "'")
       
def parse(s):
    """ Return an object representing a parsed command
        Throws ValueError for improper syntax """
    (root, remaining_tokens) = parse_tokens(s.split())
    check(len(remaining_tokens) == 0, "Expected end of command but found " + " ".join(remaining_tokens))    
    return root

# -----------------------------------------------------------------------------
# Implement the recursive parser for the Grove language
# -----------------------------------------------------------------------------

def parse_tokens(tokens):
    """ Returns a tuple:
        (an object representing the next part of the expression,
         the remaining tokens)
    """
    
    check(len(tokens) > 0)
        
    start = tokens[0]

    # TODO: complete parser with cases for each possible type of command

    
# Informal Testing Code
if __name__ == "__main__":
    # TODO: Add some tests to check if your parser works properly (Optional)
    pass
