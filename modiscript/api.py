from lexer import Lexer
from parser import Parser


class Api:
    def __init__(self, debug=False):
        self.debug = debug

    def _compile_file(self, value, valueType="filename"):
        lex_out = Lexer(value, valueType).analyze()
        if self.debug:
            with open(filename.split('.', 1)[0] + ".txt", "w") as f:
                print(*lex_out, sep='\n', file=f)
        parse_out = Parser(lex_out).parse()
        if self.debug:
            with open(filename.split('.', 1)[0] + ".py", "w") as f:
                import ast
                print(ast.dump(parse_out), file=f)
        return compile(parse_out, "<ast>", "exec")

    def execute(self, value, valueType="filename"):
        ast_module = self._compile_file(value, valueType)
        exec(ast_module)
