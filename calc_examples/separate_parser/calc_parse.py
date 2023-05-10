from calc_lang import Stmt, Expr, Name, Num, Addition, Subtraction

# Utility methods for handling parse errors
def check(condition, message = "Unexpected end of expression"):
    """ Checks if condition is true, raising a ValueError otherwise """
    if not condition:
        raise ValueError("CALC: " + message)
        
def expect(token, expected):
    """ Checks that token matches expected
        If not, throws a ValueError with explanatory message """
    if token != expected:
        check(False, "Expected '" + expected + "' but found '" + token + "'")

def is_expr(x):
    if not isinstance(x, Expr):
        check(False, "Expected expression but found " + str(type(x)))
        
# Checking for integer        
def is_int(s):
    """ Takes a string and returns True if in can be converted to an integer """
    try:
        int(s)
        return True
    except Exception:
        return False
       
def parse(s):
    """ Return an object representing a parsed command
        Throws ValueError for improper syntax """
    # get root node and leftover tokens
    root, leftover = parse_tokens(s.strip().split())

    # make sure no extra tokens
    check(len(leftover) == 0,
        "Expected end of command but found: " + " ".join(leftover))
    
    return root
        
        
def parse_tokens(tokens):
    """ Returns a tuple:
        (an object representing the next part of the expression,
         the remaining tokens)
    """
    
    check(len(tokens) > 0)
        
    start = tokens[0]
    
    if is_int(start):
        return Num(int(start)), tokens[1:]
    elif start == '+':
        check(len(tokens) >= 7)
        expect(tokens[1], '(')
        # recursively parse left expression
        left, tokens = parse_tokens(tokens[2:])
        is_expr(left)
        expect(tokens[0], ')')
        expect(tokens[1], '(')
        # recursively parse right expression
        right, tokens = parse_tokens(tokens[2:])
        is_expr(right)
        expect(tokens[0], ')')
        return Addition(left, right), tokens[1:]
    elif start == '-':
        check(len(tokens) >= 7)
        expect(tokens[1], '(')
        # recursively parse left expression
        left, tokens = parse_tokens(tokens[2:])
        is_expr(left)
        expect(tokens[0], ')')
        expect(tokens[1], '(')
        # recursively parse right expression
        right, tokens = parse_tokens(tokens[2:])
        is_expr(right)
        expect(tokens[0], ')')
        return Subtraction(left, right), tokens[1:]
    elif start == 'set':
        check(len(tokens) >= 4)
        check(tokens[1].isalpha(), "Invalid Name: " + tokens[1])
        name = Name(tokens[1])
        expect(tokens[2], '=')
        # recursive match to parse expression
        expr, tokens = parse_tokens(tokens[3:])
        is_expr(expr)
        return Stmt(name, expr), tokens
    elif start.isalpha():
        return Name(start), tokens[1:]
    else:
        check(False, "Unrecognized Command: " + start)

# Testing code
if __name__ == "__main__":
    # First try some things that should work
    cmds = [" + ( 3 ) ( 12 ) ",
            " - ( 5 ) ( 2 )",
            " + ( 15 ) ( - ( 3 ) ( 8 ) ) ",
            "set foo = 38",
            "foo",
            "set bar = + ( 22 ) ( foo )",
            "bar"]
            
    answers = [ 15,
                3,
                10,
                None,
                38,
                None,
                60 ]
    
    for i in range(0, len(cmds)):
        root = parse(cmds[i])
        result = root.eval()
        print(f"{cmds[i]} --> {result}")
        check(result == answers[i], "TEST FAILED for cmd " + cmds[i] + 
            ";  result was " + str(result) + " instead of " + str(answers[i]))
    
    # Testing for all errors is beyond our scope,
    # but we check a few
    bad_cmds = [ " ",
                 "not-alpha",
                 " + ( nope ) ( 3 ) ",
                 " 3 + 3 ",
                 " + ( 5 ) ( 4 ) foo ",
                 " + ( set x = 6 ) ( 7 )" ]
        
    for c in bad_cmds:
        try:
            root = parse(c)
            result = root.eval()
            check(False, "Did not catch an error that we should have caught")
        except Exception:
            pass