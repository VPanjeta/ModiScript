from lexer import Lexer
from parser import Parser

DEBUG = False

def compile_file(value, valueType="filename"):
    global DEBUG
    lex_out = Lexer(value, valueType).analyze()
    if DEBUG:
        with open(filename.split('.', 1)[0] + ".txt", "w") as f:
            print(*lex_out, sep='\n', file=f)
    parse_out = Parser(lex_out).parse()
    if DEBUG:
        with open(filename.split('.', 1)[0] + ".py", "w") as f:
            import ast
            print(ast.dump(parse_out), file=f)
    return compile(parse_out, "<ast>", "exec")


def execute(value, valueType="filename", debug=False):
    if debug:
        global DEBUG
        DEBUG = debug
    ast_module = compile_file(value, valueType)
    exec(ast_module)

