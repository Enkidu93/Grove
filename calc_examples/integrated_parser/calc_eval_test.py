from __future__ import annotations
import unittest

# identify the current directory of this script and add it to the path
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# import all node types from the calc language
from calc_lang import *

class TestCalcEvaluation(unittest.TestCase):
    
    def test_number(self):
        # make sure a simple number evaluates back to that number
        num: Number = Number(5)
        self.assertEqual(num.eval(), 5)

    def test_missing_name(self):
        # make sure names that do not exist produce exceptions
        with self.assertRaises(CalcEvalException):
            Name('DoesNotExist').eval()
    
    def test_set_number(self):
        # make sure the set command updates the value of a variable
        var: Name = Name('myVar')
        val1: Number = Number(5)
        val2: Number = Number(6)
        # check that a value can be initially set
        Set(var, val1).eval()
        self.assertEqual(var.eval(), val1.eval())
        # check that a value can be reset
        Set(var, val2).eval()
        self.assertEqual(var.eval(), val2.eval())
    
    def test_simple_add(self):
        num1: Number = Number(5)
        num2: Number = Number(42)
        num3: Number = Number(394)
        self.assertEqual(Add(num1, num2).eval(), 47)
        self.assertEqual(Add(num1, num3).eval(), 399)
        self.assertEqual(Add(num2, num3).eval(), 436)

    def test_simple_subtract(self):
        num1: Number = Number(5)
        num2: Number = Number(42)
        num3: Number = Number(394)
        self.assertEqual(Subtract(num2, num1).eval(), 37)
        self.assertEqual(Subtract(num1, num3).eval(), -389)
        self.assertEqual(Subtract(num3, num2).eval(), 352)
    
    def test_complex_add(self):
        # a is an add expression
        a: Expression = Add(Number(5), Number(10))
        # b is a name set to an add expression
        b: Expression = Name('other_addend')
        Set(b, Add(Number(15), Number(30))).eval()
        self.assertEqual(Add(a,b).eval(), 60)

    def test_complex_subtract(self):
        a: Expression = Add(Number(5), Add(Number(50), Number(10)))
        b: Expression = Name('subtrahend')
        Set(b, Subtract(Number(98), Number(62))).eval()
        self.assertEqual(Subtract(a,b).eval(), 29)

if __name__=='__main__': unittest.main()