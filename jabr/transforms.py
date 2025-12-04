from lark import Transformer
import sympy
from mpmath import mp

from .lexicon import special_values, postfix_operators, functions

class SympyTransformer(Transformer):
    """
    Convert a tree into a sympy expression.
    """
    def __init__(self, evaluate=True):
        self.evaluate = evaluate
        self.local_vars = {}

    def command(self, children):
        expr, *postfixes = children
        for function in postfixes:
            expr = function(expr)
        return expr

    def relation(self, children):
        rhs, op, lhs = children
        return op(rhs, lhs, evaluate=self.evaluate)

    def equals(self, children):
        return sympy.Eq

    def less_than(self, children):
        return sympy.Lt

    def greater_than(self, children):
        return sympy.Gt

    def less_than_or_equal(self, children):
        return sympy.Le

    def greater_than_or_equal(self, children):
        return sympy.Ge

    def not_equal(self, children):
        return sympy.Ne

    def assignment(self, children):
        name, expr = children
        if name == 'dps':
            mp.dps = expr
        elif name == 'prec':
            mp.prec = expr
        else:
            self.local_vars[name] = expr
        return expr

    def expression(self, children):
        terms = []
        negate_child = False
        for child in children:
            if hasattr(child, 'data') and child.data == 'plus':
                negate_child = False
            elif hasattr(child, 'data') and child.data == 'minus':
                negate_child = True
            else:
                if negate_child:
                    child = sympy.Mul(-1, child) # always evaluate
                terms.append(child)
        return sympy.Add(*terms, evaluate=self.evaluate)

    def term(self, children):
        factors = []
        invert_child = False
        for child in children:
            if hasattr(child, 'data') and child.data == 'times':
                invert_child = False
            elif hasattr(child, 'data') and child.data == 'divided_by':
                invert_child = True
            else:
                if invert_child:
                    child = sympy.Pow(child, -1, evaluate=self.evaluate)
                factors.append(child)
        return sympy.Mul(*factors, evaluate=self.evaluate)

    def factor(self, children):
        op, expr = children
        negate_child = False
        if op.data == 'plus':
            negate_child = False
        elif op.data == 'minus':
            negate_child = True
        if negate_child:
            expr = sympy.Mul(-1, expr)
        return expr

    def exponential(self, children):
        lhs, op, rhs = children
        return sympy.Pow(lhs, rhs, evaluate=self.evaluate)

    def factorial(self, children):
        expr, op = children
        if op.data == 'factorial':
            expr = sympy.factorial(expr)
        elif op.data == 'double_factorial':
            expr = sympy.factorial2(expr)
        return expr

    def function(self, children):
        name, args = children
        if name in functions:
            expr = functions[name](*args, evaluate=self.evaluate)
        elif name in postfix_operators:
            expr = postfix_operators[name](*args, evaluate=self.evaluate)
        else:
            raise ValueError(f"Unrecognized function '{name}'")
        return expr

    def postfix(self, children):
        if len(children) > 1:
            name, args = children
        else:
            name, = children
            args = []
        if name in postfix_operators:
            function = postfix_operators[name]
            def wrapper(expr):
                return function(expr, *args, evaluate=self.evaluate)
            return wrapper
        else:
            raise ValueError(f"Unrecognized postfix operator '{name}'")

    def arglist(self, children):
        return children

    def variable(self, children):
        name, = children
        if name in self.local_vars:
            return self.local_vars[name]
        elif name in special_values:
            return special_values[name]
        else:
            return sympy.Symbol(name)

    def number(self, children):
        number, = children
        try:
            return sympy.Integer(number)
        except ValueError:
            return sympy.Float(number, dps=mp.dps)

    def name(self, children):
        name, = children
        return name
