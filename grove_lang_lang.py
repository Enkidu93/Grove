from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import Any, Union
import importlib

# create a context where variables stored with set are kept
context: dict[str,int] = {}

# add a "verbose" flag to print all parse exceptions while debugging
verbose:bool = False

# define base classes for Language exceptions for ParsingExceptions
class GroveError(Exception): pass
class GroveParseError(GroveError): pass
class GroveEvalError(GroveError): pass

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
        except GroveParseError as e:
            if verbose: print(e)
        try:
            # if it is not a statement, try an expression
            return Expression.parse(tokens)
        except GroveParseError as e:
            if verbose: print(e)
        raise GroveParseError(f"Unrecognized Command: {s}")

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
            except GroveParseError as e:
                if verbose: print(e)
        # if none of the subclasses parsed successfully raise an exception
        raise GroveParseError(f"Unrecognized Expression: {' '.join(tokens)}")
    
    @classmethod
    def parse_list(cls, tokens: list[str]) -> list[Expression]:
        remaining = tokens
        out = []
        while len(remaining) != 0:
            cont = True
            index = 1
            while cont:
                toks = remaining[:index]
                try:
                    exp:Expression = Expression.parse(toks)
                    out.append(exp)
                    cont = False
                except GroveParseError as g:
                    if verbose:
                        print(g)
                    index += 1
                if index > len(remaining):
                    raise GroveParseError(f"Unrecognized Expression: {' '.join(tokens)}")
            remaining = remaining[index:]
        return out
    
    @staticmethod
    def match_parens(tokens: list[str]) -> int:
        """Searches tokens beginning with ( and returns index of matching )"""
        # ensure tokens is such that a matching ) might exist
        if len(tokens) < 2: raise GroveParseError("Expression too short")
        if tokens[0] != '(': raise GroveParseError("No opening ( found")
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
        raise GroveParseError("No closing ) found")

# define a base class for Statements
class Statement(Command, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self): pass
    @abstractmethod
    def eval(self) -> None: pass
    @classmethod
    def parse(cls, tokens: list[str]) -> Statement:
        """Factory method for creating Statement subclasses from tokens"""
        # get a list of all the subclasses of Statement
        subclasses: list[type[Statement]] = cls.__subclasses__()
        # try each subclass in turn to see if it matches the pattern
        for subclass in subclasses:
            try: 
                return subclass.parse(tokens)
            except GroveParseError as e:
                if verbose: print(e)
        # if none of the subclasses parsed successfully raise an exception
        raise GroveParseError(f"Unrecognized Expression: {' '.join(tokens)}")

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
            raise GroveParseError("Statement too short for Set")
        # 1. ensure that the very first token is "set" otherwise throw Exception
        if tokens[0] != 'set': 
            raise GroveParseError("Set statements must begin with 'set'")
        # 2. ensure that the next token is a valid Name
        try:
            name: Name = Name.parse([tokens[1]])
        except GroveParseError:
            raise GroveParseError("No name found for Set statement")
        # 3. ensure that the next token is an '='
        if tokens[2] != '=':
            raise GroveParseError("Set statement requires '='")
        # 4. ensure the remaining tokens represent an expression
        try:
            value: Expression = Expression.parse(tokens[3:])
        except GroveParseError:
            raise GroveParseError("No value found for Set statement")
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
            raise GroveParseError(f"Not enough tokens for Add in: {s}")
        # 1. ensure the first two tokens are + and (
        if tokens[0] != '+' or tokens[1] != '(':
            raise GroveParseError(f"Add must begin with '+ (' in {s}")
        # 2. ensure there is an expression inside that open parentheses
        try:
            cut = Expression.match_parens(tokens[1:])+1
            first: Expression = Expression.parse(tokens[2:cut])
        except GroveParseError:
            raise GroveParseError(f"Unable to parse first addend in: {s}")
        # 3. ensure there are enough tokens left after the first expression
        tokens = tokens[cut+1:]
        if len(tokens) < 3:
            raise GroveParseError(f"Not enough tokens left for Add in: {s}")
        # 4. ensure the first and last of the remaining tokens are ( and )
        if tokens[0] != '(' or tokens[-1] != ')':
            raise GroveParseError(f"Addends must be wrapped in ( ): {s}")
        # 5. ensure the tokens between these are a valid expression
        try:
            second: Expression = Expression.parse(tokens[1:-1])
        except GroveParseError:
            raise GroveParseError(f"Unable to parse second addend in: {s}")
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
            raise GroveParseError("Wrong number of tokens for Number")
        # 1. ensure that all characters in that token are digits
        if not tokens[0].isdigit():
            raise GroveParseError("Numbers can only contain digits")
        # if this point is reached, this is a valid Number expression
        return Number(int(tokens[0]))

# define an expression for a variable name
class Name(Expression):
    def __init__(self, name: str):
        self.name = name
    def eval(self) -> int:
        try: return context[self.name]
        except KeyError: raise GroveEvalError(f"{self.name} is undefined")
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Name) and other.name == self.name
    @staticmethod
    def parse(tokens: list[str]) -> Name:
        """Factory method for creating Name expressions from tokens"""
        # 0. ensure there is exactly one token
        if len(tokens) != 1:
            raise GroveParseError("Wrong number of tokens for Name")
        # 1. ensure that all characters in that token are alphabetic
        if not tokens[0].isidentifier():
            raise GroveParseError("Names can only contain letters, numbers, or _")
        # if this point is reached, this is a valid Number expression
        return Name(tokens[0])

class StringLiteral(Expression):
    # TODO: Implement node for String literals
    def __init__(self, word):
        self.word = word
    def eval(self):
        return self.word
    @staticmethod
    def parse(tokens: list[str]):
        if(len(tokens) != 1):
            raise GroveParseError("Invalid number of tokens for String Literal")
        token = tokens[0]
        if len(token) < 2 or token[0] != '"' or token[-1] != '"':
            raise GroveParseError("Invalid number of characters for String Literal")
        token = token[1:-1]
        if '"' in token:
            raise GroveParseError("String Literal cannot contain quote")
        for c in tokens:
            if(c == ' ' or c == '\\'):
                raise GroveParseError("String Literal cannot have white spaces")
        return StringLiteral(token)
    

class Object(Expression):
    def __init__(self, names):
        # self.name = name
        self.names:list[str] = names
    def eval(self):
        path_elements = [name.name for name in self.names]
        class_name = path_elements[-1]
        module_name = '.'.join(path_elements[0:-1])
        if verbose:
            print(module_name, class_name)
        if module_name == '__builtins__' or module_name == '':
            class_ = eval(class_name)
        else:
            try:
                module = context[module_name]
            except KeyError:
                raise GroveEvalError(f"Module {module_name} not in context.")
            try:
                class_ = getattr(module, class_name)
            except AttributeError as e:
                raise GroveEvalError(e.msg)
        return class_()
    @staticmethod
    def parse(tokens: list[str]) -> Object:
        if len(tokens) != 2:
            raise GroveParseError("Object instantiation requires two tokens.")
        if tokens[0] != "new":
            raise GroveParseError("Object instantiation must begin with 'new' keyword.")
        try:                
            name_tokens = tokens[1].split(".")
            names = []
            for name_token in name_tokens:
                names.append(Name.parse([name_token]))
            return Object(names)
        except Exception as e:
            if verbose: print(e)
            raise GroveParseError('Object instantiation failed')
    
class Call(Expression):
    # TODO: Implement node for "import" statements
    pass

class Import(Statement):
    def __init__(self, names):
        self.names:list[Name] = names
    def eval(self):
        try:
            module_name = ".".join([name.name for name in self.names])
            module = importlib.import_module(module_name)
            context[module_name] = module
        except ModuleNotFoundError as m:
            raise GroveEvalError(f"Module not found: {m.msg}")
    @staticmethod
    def parse(tokens: list[str]) -> Object:
        if len(tokens) != 2:
            raise GroveParseError("Not enough tokens for import statement")
        if tokens[0] != "import":
            raise GroveParseError("Import statement must begin with 'import' keyword.")
        try:                
            name_tokens = tokens[1].split(".")
            names = []
            for name_token in name_tokens:
                names.append(Name.parse([name_token]))
            return Import(names)
        except Exception as e:
            if verbose: print(e)
            raise GroveParseError('Not enough tokens to be import statement')
        

class Terminate(Statement):
	# TODO: Implement node for "quit" and "exit" statements
    def __init__(self, word):
        self.keyword = word
    def eval(self): 
        if self.keyword == "quit" or self.keyword == "exit":
            quit()
        else:
            raise GroveEvalError("Invalid keyword")
    @staticmethod
    def parse(tokens: list[str]) -> Expression:
        """Factory method for creating Terminate commands from tokens"""
        # check to see if this string matches the pattern for terminate
        # 0. ensure there are enough tokens for this to be a terminate statement
        if len(tokens) != 1:
            raise GroveParseError("Statement too long for Terminate")
        # 1. ensure that the only token is "quit" or "exit"
        keyword = tokens[0]
        if keyword != 'quit' and keyword != 'exit': 
            raise GroveParseError("Terminate statements must be 'quit' or 'exit'")
        return Terminate(keyword)