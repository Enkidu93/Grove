## Parse tree nodes for the Calc language
import re
import sys
import importlib
import builtins

# The exception classes from the notes.
class GroveError(Exception): pass
class GroveParseError(GroveError): pass
class GroveEvalError(GroveError): pass

# Command Base Class (superclass of expressions and statements)
class Command(object):
    pass

# Expression Base Class (superclass of Num, Name, StringLiteral, etc.)
class Expression(Command):
    pass

# Statement Base Class (superclass of Assign, Terminate, and Import)
class Statement(Command):
    pass

# -----------------------------------------------------------------------------
# Implement each of the following parse tree nodes for the Grove language
# -----------------------------------------------------------------------------

class Number(Expression):
	# TODO: Implement node for Number literals
	pass

class StringLiteral(Expression):
    # TODO: Implement node for String literals
    pass

class Object(Expression):
	# TODO: Implement node for "new" expression
    pass
    
class Call(Expression):
    # TODO: Implement node for "call" expression
    pass
        
class Addition(Expression):
    # TODO: Implement node for "+"
    pass

class Name(Expression):
    # TODO: Implement node for <Name> expressions
    pass

class Assignment(Expression):
	# TODO: Implement node for "set" statements
	pass

class Import(Expression):
    # TODO: Implement node for "import" statements
    pass

class Terminate(Expression):
	# TODO: Implement node for "quit" and "exit" statements
    
	pass
