from sympy.printing import StrPrinter

class CustomPrinter(StrPrinter):
    def _print_Infinity(self, expr):
        return '∞'

    def _print_NegativeInfinity(self, expr):
        return '-∞'

    def _print_ComplexInfinity(self, expr):
        return 'z∞'

    def _print_ImaginaryUnit(self, expr):
        return 'i'

    def _print_Pi(self, expr):
        return 'π'

    def _print_Exp1(self, expr):
        return 'e'

    def _print_EulerGamma(self, expr):
        return 'γ'

    def _print_Abs(self, expr):
        return f'abs({self._print(expr.args[0])})'

    def _print_gamma(self, expr):
        return f'Γ({self._print(expr.args[0])})'

    def _print_digamma(self, expr):
        return f'ψ({self._print(expr.args[0])})'

    def _print_zeta(self, expr):
        return f'ζ({self._print(expr.args[0])})'

    def _print_factorial(self, expr):
        arg = expr.args[0]
        if (arg.is_Integer and arg.is_nonnegative) or arg.is_Symbol:
            return f'{self._print(arg)}!'
        else:
            return f'({self._print(arg)})!'

    def _print_factorial2(self, expr):
        arg = expr.args[0]
        if (arg.is_Integer and arg.is_nonnegative) or arg.is_Symbol:
            return f'{self._print(expr.args[0])}!!'
        else:
            return f'({self._print(arg)})!!'
