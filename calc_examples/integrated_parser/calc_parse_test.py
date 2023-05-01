from __future__ import annotations
import unittest

# identify the current directory of this script and add it to the path
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# import all node types from the calc language
from calc_lang import *

class TestCalcParsing(unittest.TestCase):
    
    def test_number(self):
        cmd: Command = Command.parse("64")
        self.assertEqual(cmd, Number(64))
    
    def test_name(self):
        cmd: Command = Command.parse("hello")
        self.assertEqual(cmd, Name("hello"))
    
    def test_simple_set(self):
        cmd: Command = Command.parse("set hello = 64")
        self.assertEqual(cmd, Set(Name("hello"), Number(64)))
    
    def test_simple_add(self):
        cmd1: Command = Command.parse("+ ( 42 ) ( 64 )")
        self.assertEqual(cmd1, Add(Number(42), Number(64)))
        cmd2: Command = Command.parse("+ ( hello ) ( world )")
        self.assertEqual(cmd2, Add(Name("hello"), Name("world")))
        cmd3: Command = Command.parse("+ ( blue ) ( 42 )")
        self.assertEqual(cmd3, Add(Name("blue"), Number(42)))

    def test_simple_subtract(self):
        cmd1: Command = Command.parse("- ( 42 ) ( 64 )")
        self.assertEqual(cmd1, Subtract(Number(42), Number(64)))
        cmd2: Command = Command.parse("- ( hello ) ( world )")
        self.assertEqual(cmd2, Subtract(Name("hello"), Name("world")))
        cmd3: Command = Command.parse("- ( blue ) ( 42 )")
        self.assertEqual(cmd3, Subtract(Name("blue"), Number(42)))
    
    def test_nested_add(self):
        cmd: Command = Command.parse("+ ( - ( 15 ) ( 5 ) ) ( + ( 1 ) ( 3 ) )")
        ans: Command = Add(Subtract(Number(15),Number(5)),Add(Number(1),Number(3)))
        self.assertEqual(cmd, ans)
    
    def test_nested_subtract(self):
        cmd: Command = Command.parse("- ( - ( 15 ) ( 5 ) ) ( + ( 1 ) ( 3 ) )")
        ans: Command = Subtract(Subtract(Number(15),Number(5)),Add(Number(1),Number(3)))
        self.assertEqual(cmd, ans)

    def test_complex_set(self):
        cmd: Command = Command.parse("set x = + ( + ( 1 ) ( 2 ) ) ( hello )")
        self.assertEqual(cmd, Set(Name("x"), Add(Add(Number(1),Number(2)),Name("hello"))))
        

if __name__=='__main__': unittest.main()