from .lexer import Lexer
from .parser import Parser


class ModiScript:
    def __init__(self, debug=False):
        self.debug = debug

    def _compile_file(self, value, value_type="filename"):
        lex_out = Lexer(value, value_type).analyze()
        if self.debug and value_type == "filename":
            filename = value
            with open(filename.split('.', 1)[0] + ".txt", "w") as f:
                print(*lex_out, sep='\n', file=f)
        parse_out = Parser(lex_out).parse()
        if self.debug and value_type == "filename":
            with open(filename.split('.', 1)[0] + ".py", "w") as f:
                import ast
                print(ast.dump(parse_out), file=f)
        return compile(parse_out, "<ast>", "exec")

    def execute(self, value, value_type="filename"):
        ast_module = self._compile_file(value, value_type)
        exec(ast_module)
