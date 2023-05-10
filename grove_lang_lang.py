from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import Any, Union
import importlib

# create a context where variables stored with set are kept
context: dict[str,int] = {}

# add a "verbose" flag to print all parse exceptions while debugging
verbose = False

# define base classes for Language exceptions for ParsingExceptions
class GroveLangException(Exception): pass
class GroveLangParseException(GroveLangException): pass
class GroveLangEvalException(GroveLangException): pass

# define a base class for Commands
class Command(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self): pass
    @abstractmethod
    def eval(self) -> Union[int,None]: pass
    @staticmethod
    def parse(s: str) -> Command:
        """Factory method for creating Command subclasses from lines of code"""
        # the command should split the input into tokens based on whitespace
        tokens: list[str] = s.strip().split()
        # a command must be either a statement or an expression
        try:
            # first try to parse the command as a statement
            return Statement.parse(tokens)
        except GroveLangParseException as e:
            if verbose: print(e)
        try:
            # if it is not a statement, try an expression
            return Expression.parse(tokens)
        except GroveLangParseException as e:
            if verbose: print(e)
        raise GroveLangParseException(f"Unrecognized Command: {s}")

# define a base class for Expressions
class Expression(Command, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self): pass
    @abstractmethod
    def eval(self) -> int: pass
    @classmethod
    def parse(cls, tokens: list[str]) -> Expression:
        """Factory method for creating Expression subclasses from tokens"""
        # get a list of all the subclasses of Expression
        subclasses: list[type[Expression]] = cls.__subclasses__()
        # try each subclass in turn to see if it matches the pattern
        for subclass in subclasses:
            try: 
                return subclass.parse(tokens)
            except GroveLangParseException as e:
                if verbose: print(e)
        # if none of the subclasses parsed successfully raise an exception
        raise GroveLangParseException(f"Unrecognized Expression: {' '.join(tokens)}")
    @staticmethod
    def match_parens(tokens: list[str]) -> int:
        """Searches tokens beginning with ( and returns index of matching )"""
        # ensure tokens is such that a matching ) might exist
        if len(tokens) < 2: raise GroveLangParseException("Expression too short")
        if tokens[0] != '(': raise GroveLangParseException("No opening ( found")
        # track the depth of nested ()
        depth: int = 0
        for i,token in enumerate(tokens):
            # when a ( is found, increase the depth
            if token == '(': depth += 1
            # when a ) is found, decrease the depth
            elif token == ')': depth -= 1
            # if after a token the depth reaches 0, return that index
            if depth == 0: return i
        # if the depth never again reached 0 then parens do not match
        raise GroveLangParseException("No closing ) found")

# define a base class for Statements
class Statement(Command, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self): pass
    @abstractmethod
    def eval(self) -> None: pass
    @staticmethod
    def parse(tokens: list[str]) -> Statement:
        """Factory method for creating Statement subclasses from tokens"""
        # the only valid statement in our language is set so try that
        stmt: Statement = Set.parse(tokens)
        return stmt

# define a class to represent the "set" statement
class Set(Statement):
    def __init__(self, name: Name, value: Expression):
        self.name = name
        self.value = value
    def eval(self) -> None:
        context[self.name.name] = self.value.eval()
    def __eq__(self, other: Any):
        return (isinstance(other, Set) and 
                self.name == other.name and 
                self.value == other.value)
    @staticmethod
    def parse(tokens: list[str]) -> Set:
        """Factory method for creating Set commands from tokens"""
        # check to see if this string matches the pattern for set
        # 0. ensure there are enough tokens for this to be a set statement
        if len(tokens) < 4:
            raise GroveLangParseException("Statement too short for Set")
        # 1. ensure that the very first token is "set" otherwise throw Exception
        if tokens[0] != 'set': 
            raise GroveLangParseException("Set statements must begin with 'set'")
        # 2. ensure that the next token is a valid Name
        try:
            name: Name = Name.parse([tokens[1]])
        except GroveLangParseException:
            raise GroveLangParseException("No name found for Set statement")
        # 3. ensure that the next token is an '='
        if tokens[2] != '=':
            raise GroveLangParseException("Set statement requires '='")
        # 4. ensure the remaining tokens represent an expression
        try:
            value: Expression = Expression.parse(tokens[3:])
        except GroveLangParseException:
            raise GroveLangParseException("No value found for Set statement")
        # if this point is reached, this is a valid Set statement
        return Set(name, value)

# define an expression for the addition operation
class Add(Expression):
    def __init__(self, first: Expression, second: Expression):
        self.first = first
        self.second = second
    def eval(self) -> int:
        return self.first.eval() + self.second.eval()
    def __eq__(self, other) -> bool:
        return (isinstance(other, Add) and 
                other.first == self.first and 
                other.second == self.second)
    @staticmethod
    def parse(tokens: list[str]) -> Add:
        """Factory method for creating Add expressions from tokens"""
        s = ' '.join(tokens)
        # check to see if this string matches the pattern for add
        # 0. ensure there are enough tokens for this to be a add expression
        if len(tokens) < 7:
            raise GroveLangParseException(f"Not enough tokens for Add in: {s}")
        # 1. ensure the first two tokens are + and (
        if tokens[0] != '+' or tokens[1] != '(':
            raise GroveLangParseException(f"Add must begin with '+ (' in {s}")
        # 2. ensure there is an expression inside that open parentheses
        try:
            cut = Expression.match_parens(tokens[1:])+1
            first: Expression = Expression.parse(tokens[2:cut])
        except GroveLangParseException:
            raise GroveLangParseException(f"Unable to parse first addend in: {s}")
        # 3. ensure there are enough tokens left after the first expression
        tokens = tokens[cut+1:]
        if len(tokens) < 3:
            raise GroveLangParseException(f"Not enough tokens left for Add in: {s}")
        # 4. ensure the first and last of the remaining tokens are ( and )
        if tokens[0] != '(' or tokens[-1] != ')':
            raise GroveLangParseException(f"Addends must be wrapped in ( ): {s}")
        # 5. ensure the tokens between these are a valid expression
        try:
            second: Expression = Expression.parse(tokens[1:-1])
        except GroveLangParseException:
            raise GroveLangParseException(f"Unable to parse second addend in: {s}")
        # if this point is reached, this is a valid Add expression
        return Add(first, second)
    #TODO CHECK TYPE MISMATCH

# define an expression for an integer constant
class Number(Expression):
    def __init__(self, num: int):
        self.num = num
    def eval(self) -> int:
        return self.num
    def __eq__(self, other: Any) -> bool:
        return (isinstance(other, Number) and other.num == self.num)
    @staticmethod
    def parse(tokens: list[str]) -> Number:
        """Factory method for creating Number expressions from tokens"""
        # 0. ensure there is exactly one token
        if len(tokens) != 1:
            raise GroveLangParseException("Wrong number of tokens for Number")
        # 1. ensure that all characters in that token are digits
        if not tokens[0].isdigit():
            raise GroveLangParseException("Numbers can only contain digits")
        # if this point is reached, this is a valid Number expression
        return Number(int(tokens[0]))

# define an expression for a variable name
class Name(Expression):
    def __init__(self, name: str):
        self.name = name
    def eval(self) -> int:
        try: return context[self.name]
        except KeyError: raise GroveLangEvalException(f"{self.name} is undefined")
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Name) and other.name == self.name
    @staticmethod
    def parse(tokens: list[str]) -> Name:
        """Factory method for creating Name expressions from tokens"""
        # 0. ensure there is exactly one token
        if len(tokens) != 1:
            raise GroveLangParseException("Wrong number of tokens for Name")
        # 1. ensure that all characters in that token are alphabetic
        if not tokens[0].isalpha():
            raise GroveLangParseException("Names can only contain letters")
        # if this point is reached, this is a valid Number expression
        return Name(tokens[0])

class StringLiteral(Expression):
    # TODO: Implement node for String literals
    def __init__(self, word):
        self.word = word
    def eval(self):
        for c in self.word:
            if(c == ' '):
                return GroveLangEvalException
        return self.word
    @staticmethod
    def parse(tokens: list[str]):
        raise GroveLangParseException
        # for str in tokens:
        #     eval(str)

class Object(Expression):
    def __init__(self, value):
        # self.name = name
        self.value = value
    def eval(self):
        return self.value
    @staticmethod
    def parse(tokens: list[str]) -> Object:
        if len(tokens) < 2:
            raise GroveLangParseException("Too short for Object instantiation")
        if tokens[0] != "new":
            raise GroveLangParseException("Object instantiation must begin with 'new' keyword.")
        try:                
            path_elements = tokens[1].split(".")
            if len(path_elements) == 1:
                class_ = eval(tokens[1])
            else:
                class_name = path_elements[-1]
                module_name = '.'.join(path_elements[0:-1])
                if verbose:
                    print(module_name, class_name)
                if module_name == '__builtins__':
                    class_ = eval(class_name)
                else:
                    module = importlib.import_module(module_name)
                    class_ = getattr(module, class_name)
            instance = class_()
        except Exception as e:
            if verbose: print(e)
            raise GroveLangParseException('Object instantiation failed')
        return Object(instance)

    
class Call(Expression):
    # TODO: Implement node for "call" expression
    pass

class Import(Expression):
    # TODO: Implement node for "import" statements
    pass

class Terminate(Expression):
	# TODO: Implement node for "quit" and "exit" statements
    def __init__(self, word):
        self.word = word
    def eval(self): 
        if self.keyword == "quit" or self.keyword == "exit":
            quit()
        else:
            raise GroveLangEvalException("Invalid keyword")
    @staticmethod
    def parse(tokens: list[str]) -> Expression:
        """Factory method for creating Terminate commands from tokens"""
        # check to see if this string matches the pattern for terminate
        # 0. ensure there are enough tokens for this to be a terminate statement
        if len(tokens) != 1:
            raise GroveLangParseException("Statement too long for Terminate")
        # 1. ensure that the only token is "quit" or "exit"
        keyword = tokens[0]
        if keyword != 'quit' and keyword != 'exit': 
            raise GroveLangParseException("Terminate statements must be 'quit' or 'exit'")
        return Terminate(keyword)