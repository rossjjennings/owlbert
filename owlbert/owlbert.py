from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit import print_formatted_text as print_formatted
from lark import Lark, UnexpectedInput
from pathlib import Path
import sympy
from sympy.printing import StrPrinter

from .compiler import compile_expression

kb = KeyBindings()
with open(Path(__file__).parent / "grammar.lark") as f:
    grammar = Lark(f.read(), parser='lalr')

@kb.add('c-j')
def add_line(event):
    event.current_buffer.insert_text('\n')

@kb.add('c-m')
def accept_input(event):
    event.current_buffer.validate_and_handle()

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
    def _print_Abs(self, expr):
        return f'abs({self._print(expr.args[0])})'

def run_repl():
    session = PromptSession()
    print()

    i = 1
    while True:
        try:
            input_text = session.prompt(
                HTML(f"<ansibrightgreen>In [<b>{i}</b>]:</ansibrightgreen> "),
                key_bindings=kb,
                multiline=True,
            )
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            try:
                tree = grammar.parse(input_text)
            except UnexpectedInput as err:
                print_formatted(HTML(f"<ansibrightred>{'-'*75}</ansibrightred>"))
                msg = "<b>ERROR</b>: Got unexpected input while parsing"
                print_formatted(HTML(f"<ansibrightred>{msg}</ansibrightred>"))
                print_formatted(HTML(f"<ansibrightred>{'-'*75}</ansibrightred>"))
                print(str(err))
                continue
            try:
                result = compile_expression(tree)
            except ValueError as err:
                print_formatted(HTML(f"<ansibrightred>{'-'*75}</ansibrightred>"))
                msg = "<b>ERROR</b>: Could not evaluate expression"
                print_formatted(HTML(f"<ansibrightred>{msg}</ansibrightred>"))
                print_formatted(HTML(f"<ansibrightred>{'-'*75}</ansibrightred>"))
                print(str(err))
                print()
                continue

            result_str = CustomPrinter().doprint(result)
            if isinstance(result, sympy.Float):
                if '.' in result_str:
                    result_str = result_str.rstrip("0")
            print_formatted(HTML(f"<ansibrightred>Out[<b>{i}</b>]:</ansibrightred> {result_str}\n"))
            i += 1

if __name__ == "__main__":
    run_repl()
