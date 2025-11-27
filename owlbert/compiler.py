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
            if token.value in ['pi', 'π']:
                return sympy.pi
            elif token.value in ['e', 'E']:
                return sympy.E
            elif token.value in ['i', 'I']:
                return sympy.I
            elif token.value in ['inf', 'oo', '∞']:
                return sympy.oo
            elif token.value in ['zinf', 'zoo', 'z∞']:
                return sympy.zoo
            elif token.value == 'nan':
                return sympy.nan
            else:
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
                case "trigsimp":
                    value = sympy.trigsimp(value)
                case "expand_trig" | "trigexpand":
                    value = sympy.expand_trig(value)
                case "powsimp":
                    value = sympy.powsimp(value)
                case "expand_power_exp" | "expexpand":
                    value = sympy.expand_power_exp(value)
                case "expand_power_base" | "baseexpand":
                    value = sympy.expand_power_base(value)
                case "powdenest":
                    value = sympy.powdenest(value)
                case "expand_log" | "logexpand":
                    value = sympy.expand_log(value)
                case "logcombine":
                    value = sympy.logcombine(value)
                case "expand_func" | "funcexpand":
                    value = sympy.expand_func(value)
                case "gammasimp":
                    value = sympy.gammasimp(value)
                case "complexexpand":
                    value = value.expand(complex=True)
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
        elif tree.data == 'function':
            name = tree.children[0].value
            value = compile_expression(tree.children[1])
            match name:
                case "exp":
                    value = sympy.exp(value)
                case "log":
                    value = sympy.log(value)
                case "sqrt":
                    value = sympy.sqrt(value)
                case "cbrt":
                    value = sympy.cbrt(value)
                case "re":
                    value = sympy.re(value)
                case "im":
                    value = sympy.im(value)
                case "abs":
                    value = sympy.Abs(value)
                case "arg":
                    value = sympy.arg(value)
                case "conj" | "conjugate":
                    value = sympy.conjugate(value)
                case "sin":
                    value = sympy.sin(value)
                case "cos":
                    value = sympy.cos(value)
                case "tan":
                    value = sympy.tan(value)
                case "cot":
                    value = sympy.cot(value)
                case "sec":
                    value = sympy.sec(value)
                case "csc":
                    value = sympy.csc(value)
                case "sinc":
                    value = sympy.sinc(value)
                case "asin" | "arcsin":
                    value = sympy.asin(value)
                case "acos" | "arccos":
                    value = sympy.acos(value)
                case "atan" | "arctan":
                    value = sympy.atan(value)
                case "acot" | "arccot":
                    value = sympy.acot(value)
                case "asec" | "arcsec":
                    value = sympy.asec(value)
                case "acsc" | "arccsc":
                    value = sympy.acsc(value)
                case "sinh":
                    value = sympy.sinh(value)
                case "cosh":
                    value = sympy.cosh(value)
                case "tanh":
                    value = sympy.tanh(value)
                case "coth":
                    value = sympy.coth(value)
                case "sech":
                    value = sympy.sech(value)
                case "csch":
                    value = sympy.csch(value)
                case "asinh" | "arsinh":
                    value = sympy.asinh(value)
                case "acosh" | "arcosh":
                    value = sympy.acosh(value)
                case "atanh" | "artanh":
                    value = sympy.atanh(value)
                case "acoth" | "arcoth":
                    value = sympy.acoth(value)
                case "asech" | "arsech":
                    value = sympy.asech(value)
                case "acsch" | "arcsch":
                    value = sympy.acsch(value)
                case "W" | "LambertW":
                    value = sympy.LambertW(value)
                case "gamma":
                    value = sympy.gamma(value)
                case "digamma":
                    value = sympy.digamma(value)
                case "trigamma":
                    value = sympy.trigamma(value)
                case "erf":
                    value = sympy.erf(value)
                case "erfc":
                    value = sympy.erfc(value)
                case "erfinv":
                    value = sympy.erfinv(value)
                case "erfcinv":
                    value = sympy.erfcinv(value)
                case "zeta":
                    value = sympy.zeta(value)
            return value
