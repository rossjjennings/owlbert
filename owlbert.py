from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit import print_formatted_text as print_formatted
from lark import Lark, UnexpectedToken

kb = KeyBindings()
with open("grammar.lark") as f:
    grammar = Lark(f.read(), parser='lalr')

@kb.add('c-j')
def add_line(event):
    event.current_buffer.insert_text('\n')

@kb.add('c-m')
def accept_input(event):
    event.current_buffer.validate_and_handle()

def run_repl():
    session = PromptSession()

    i = 1
    while True:
        try:
            input_text = session.prompt(HTML(f"<ansibrightgreen>[<b>{i}</b>]:</ansibrightgreen> "),
                                  key_bindings=kb, multiline=True)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            try:
                result = grammar.parse(input_text).pretty()
            except UnexpectedToken as err:
                result = str(err)
            print(f"{result}\n")
            i += 1

if __name__ == "__main__":
    run_repl()
