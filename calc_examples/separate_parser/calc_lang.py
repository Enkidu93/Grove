## Parse tree nodes for the Calc language

var_table = {}

class Expr:
    pass
    
class Num(Expr):
    def __init__(self, val):
        self.val = val
    def eval(self):
        return self.val
        
class Addition(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def eval(self):
        return self.left.eval() + self.right.eval()
        
class Subtraction(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def eval(self):
        return self.left.eval() - self.right.eval()
        
        
class Name(Expr):
    def __init__(self, val):
        self.val = val
    def eval(self):
        return var_table[self.val]
        
class Stmt:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    def eval(self):
        val = self.expr.eval()
        var_table[self.name.val] = val
        return None
        

# some testing code
if __name__ == "__main__":
    assert(Num(3).eval() == 3)
    assert(Addition(Num(3), Num(10)).eval() == 13)
    assert(Subtraction(Num(3), Num(10)).eval() == -7)
    
    caught_error = False
    try:
        print(Name("nope").eval())
    except Exception:
        caught_error = True
    assert(caught_error)
    
    assert(Stmt(Name("foo"), Num(10)).eval() is None)
    assert(Name("foo").eval() == 10)
    
    # Try something more complicated
    assert(Stmt(Name("foo"), Addition(Num(200), Subtraction(Num(4), Num(12)))).eval() is None)
    assert(Name("foo").eval() == 192)