from lark import Tree, Token
import sympy
from sympy import Symbol, Integer, Float
from operator import mul
from functools import reduce

def get_symbols(tree):
    """
    Get a dictionary of sympy Symbol objects for each CNAME token
    in the input tree.
    """
    def is_cname(node):
        return isinstance(node, Token) and node.type == 'CNAME'

    symbols = {}
    for token in tree.scan_values(is_cname):
        if not token.value in symbols:
            symbols[token.value] = Symbol(token.value)

    return symbols

def compile_expression(tree):
    if isinstance(token := tree, Token):
        if token.type == 'CNAME':
            return Symbol(token.value)
        elif token.type == 'NUMBER':
            try:
                return Integer(token.value)
            except ValueError:
                return Float(token.value)
        else:
            raise ValueError(f"unrecognized token type '{token.type}'")
    elif isinstance(tree, Tree):
        if tree.data == 'start':
            first_child = tree.children[0]
            value = compile_expression(first_child)
            last_child = tree.children[-1]
            match last_child.value:
                case "N" | "evalf":
                    value = value.evalf()
                case "simplify":
                    value = sympy.simplify(value)
                case "expand":
                    value = sympy.expand(value)
                case "factor":
                    value = sympy.factor(value)
                case "cancel":
                    value = sympy.cancel(value)
                case "apart":
                    value = sympy.apart(value)
            return value
        elif tree.data == 'expression':
            terms = []
            negate_child = False
            for child in tree.children:
                if isinstance(child, Tree) and child.data == 'plus':
                    negate_child = False
                elif isinstance(child, Tree) and child.data == 'minus':
                    negate_child = True
                else:
                    child_value = compile_expression(child)
                    if negate_child:
                        child_value = -child_value
                    terms.append(child_value)
            return sum(terms)
        elif tree.data == 'term':
            factors = []
            invert_child = False
            for child in tree.children:
                if isinstance(child, Tree) and child.data == 'times':
                    invert_child = False
                elif isinstance(child, Tree) and child.data == 'divided_by':
                    invert_child = True
                else:
                    child_value = compile_expression(child)
                    if invert_child:
                        child_value = 1/child_value
                    factors.append(child_value)
            return reduce(mul, factors)
        elif tree.data == 'factor':
            negate_child = False
            first_child = tree.children[0]
            if isinstance(first_child, Tree) and first_child.data == 'plus':
                negate_child = False
            elif isinstance(first_child, Tree) and first_child.data == 'minus':
                negate_child = True
            last_child = tree.children[-1]
            child_value = compile_expression(last_child)
            if negate_child:
                child_value = -child_value
            return child_value
        elif tree.data == 'exponential':
            first_child = tree.children[0]
            base_value = compile_expression(first_child)
            if len(tree.children) > 1:
                last_child = tree.children[-1]
                exp_value = compile_expression(last_child)
                return base_value**exp_value
            else:
                return base_value
