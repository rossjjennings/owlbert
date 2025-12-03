from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit import print_formatted_text as print_formatted
from lark import Lark, UnexpectedInput
from pathlib import Path
import sympy
from mpmath import mp

from .compiler import compile_expression
from .completion import LatexCompleter
from .printing import CustomPrinter

kb = KeyBindings()
with open(Path(__file__).parent / "grammar.lark") as f:
    grammar = Lark(f.read(), parser='lalr')

@kb.add('c-j')
def add_line(event):
    event.current_buffer.insert_text('\n')

@kb.add('c-m')
def accept_input(event):
    event.current_buffer.validate_and_handle()

def run():
    session = PromptSession(completer=LatexCompleter())
    print()

    i = 1
    local_vars = {}
    while True:
        local_vars['dps'] = sympy.Integer(mp.dps)
        local_vars['prec'] = sympy.Integer(mp.prec)
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
                result = compile_expression(tree, local_vars)
            except Exception as err:
                print_formatted(HTML(f"<ansibrightred>{'-'*75}</ansibrightred>"))
                msg = "<b>ERROR</b>: Could not evaluate expression"
                print_formatted(HTML(f"<ansibrightred>{msg}</ansibrightred>"))
                print_formatted(HTML(f"<ansibrightred>{'-'*75}</ansibrightred>"))
                print(str(err))
                print()
                continue

            local_vars['_'] = result
            result_str = CustomPrinter().doprint(result)
            print_formatted(HTML("<ansibrightred>Out[<b>{}</b>]:</ansibrightred> {}\n").format(i, result_str))
            i += 1

if __name__ == "__main__":
    run()
