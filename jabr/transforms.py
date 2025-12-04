from lark import Transformer
import sympy
from mpmath import mp

from .lexicon import special_values, postfix_operators, functions

rel_ops = {
    'equals': sympy.Eq,
    'less_than': sympy.Lt,
    'greater_than': sympy.Gt,
    'less_than_or_equal': sympy.Le,
    'greater_than_or_equal': sympy.Ge,
    'not_equal': sympy.Ne,
}

class SympyTransformer(Transformer):
    """
    Convert a tree into a sympy expression.
    """
    def __init__(self):
        self.local_vars = {}

    def command(self, children):
        expr, *postfixes = children
        for name in postfixes:
            if name in postfix_operators:
                expr = postfix_operators[name](expr)
        return expr

    def relation(self, children):
        rhs, op, lhs = children
        return op(rhs, lhs)

    def rel_op(self, children):
        data, = children
        return rel_ops[data]

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
                    child = sympy.Mul(-1, child)
                terms.append(child)
        return sympy.Add(*terms)

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
                    child = sympy.Pow(child, -1)
                factors.append(child)
        return sympy.Mul(*factors)

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
        return sympy.Pow(lhs, rhs)

    def factorial(self, children):
        expr, op = children
        if op.data == 'factorial':
            expr = sympy.factorial(expr)
        elif op.data == 'double_factorial':
            expr = sympy.factorial2(expr)
        return expr

    def function(self, children):
        name, *args = children
        if name in functions:
            expr = functions[name](*args)
        elif name in postfix_operators:
            expr = postfix_operators[name](*args)
        else:
            raise ValueError(f"Unrecognized function '{name}'")
        return expr

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
