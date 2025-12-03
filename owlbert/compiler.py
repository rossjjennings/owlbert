from lark import Tree, Token
import sympy
from sympy import Symbol, Integer, Float
from mpmath import mp
from operator import mul
from functools import reduce

from .lexicon import special_values, postfix_operators, functions

def compile_expression(tree, local_vars):
    if isinstance(token := tree, Token):
        if token.type == 'CNAME':
            if token.value in local_vars:
                return local_vars[token.value]
            elif token.value in special_values:
                return special_values[token.value]
            else:
                return Symbol(token.value)
        elif token.type == 'NUMBER':
            try:
                return Integer(token.value)
            except ValueError:
                return Float(token.value, dps=mp.dps)
        else:
            raise ValueError(f"unrecognized token type '{token.type}'")
    elif isinstance(tree, Tree):
        if tree.data == 'command':
            first_child = tree.children[0]
            value = compile_expression(first_child, local_vars)
            for child in tree.children[1:]:
                if hasattr(child, 'value') and child.value == "//":
                    pass
                elif hasattr(child, 'data') and child.data == 'function':
                    name = child.children[0].value
                    args = [value] + [
                        compile_expression(grandchild, local_vars)
                        for grandchild in child.children[1:]
                    ]
                    if name in postfix_operators:
                        value = postfix_operators[name](*args)
                    else:
                        raise ValueError(f"Unrecognized postfix operator '{name}'")
                elif hasattr(child, 'value'):
                    name = child.value
                    if child.value in postfix_operators:
                        value = postfix_operators[child.value](value)
                    else:
                        raise ValueError(f"Unrecognized postfix operator '{name}'")
            return value
        elif tree.data == 'relation':
            lhs = tree.children[0]
            lhs_value = compile_expression(lhs, local_vars)
            rhs = tree.children[2] # should exist since otherwise the node is omitted
            rhs_value = compile_expression(rhs, local_vars)
            match tree.children[1].data:
                case 'equals':
                    return sympy.Eq(lhs_value, rhs_value)
                case 'less_than':
                    return sympy.Lt(lhs_value, rhs_value)
                case 'greater_than':
                    return sympy.Gt(lhs_value, rhs_value)
                case 'less_than_or_equal':
                    return sympy.Le(lhs_value, rhs_value)
                case 'greater_than_or_equal':
                    return sympy.Ge(lhs_value, rhs_value)
                case 'not_equal':
                    return sympy.Ne(lhs_value, rhs_value)
        elif tree.data == 'assignment':
            name = tree.children[0].value
            value = compile_expression(tree.children[1], local_vars)
            if name == 'dps':
                mp.dps = value
            elif name == 'prec':
                mp.prec = value
            else:
                local_vars[name] = value
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
                    child_value = compile_expression(child, local_vars)
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
                    child_value = compile_expression(child, local_vars)
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
            child_value = compile_expression(last_child, local_vars)
            if negate_child:
                child_value = -child_value
            return child_value
        elif tree.data == 'exponential':
            first_child = tree.children[0]
            base_value = compile_expression(first_child, local_vars)
            if len(tree.children) > 1:
                last_child = tree.children[-1]
                exp_value = compile_expression(last_child, local_vars)
                return base_value**exp_value
            else:
                return base_value
        elif tree.data == 'factorial':
            value = compile_expression(tree.children[0], local_vars)
            if tree.children[1].data == 'factorial':
                value = sympy.factorial(value)
            elif tree.children[1].data == 'double_factorial':
                value = sympy.factorial2(value)
            return value
        elif tree.data == 'function':
            name = tree.children[0].value
            args = [compile_expression(child, local_vars) for child in tree.children[1:]]
            if name in functions:
                value = functions[name](*args)
            elif name in postfix_operators:
                value = postfix_operators[name](*args)
            else:
                raise ValueError(f"Unrecognized function '{name}'")
            return value
