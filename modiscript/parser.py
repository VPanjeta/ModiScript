from ast import *
from .utils import LEX, ErrorHandler, ERROR, CONGRESS_RULE


class Parser:
    def __init__(self, lex):
        self.lex = lex
        self.length = len(lex)
        self._variables = set()

    def parse(self):
        """
        Convert to ast
        """
        module = self._analyze_module()
        fix_missing_locations(module)
        return module

    def _debug_details(self, num):
        if isinstance(num, dict):
            return {'lineno': num['line'], 'col_offset': num['offset']}
        return {'lineno': self.lex[num]['line'], 'col_offset': self.lex[num]['offset']}

    def _load_var(self, num):
        return Name(id=self.lex[num]['value'], ctx=Load(), **self._debug_details(num))

    def _store_var(self, num):
        return Name(id=self.lex[num]['value'], ctx=Store(), **self._debug_details(num))

    def _is_not(self, lex):
        if isinstance(lex, int):
            lex = self.lex[lex]
        return lex['lex'] == LEX['var'] and lex['value'] == 'nahi'

    def _analyze(self, num):
        """
        Begin a new line.
        """
        lexeme = self.lex[num]
        if lexeme['lex'] == LEX['if']:
            return self._analyze_if(num)
        if lexeme['lex'] == LEX['until']:
            return self._analyze_until(num)
        if lexeme['lex'] == LEX['print']:
            return self._analyze_print(num)
        if lexeme['lex'] == LEX['input']:
            return self._analyze_input(num)
        if lexeme['lex'] == LEX['var']:
            return self._analyze_assign(num)
        return num + 1, None

    def _analyze_module(self):
        code = []
        num = 0
        while num < self.length:
            num, node = self._analyze(num)
            if node is not None:
                code.append(node)
        return Module(body=code, **self._debug_details(0))

    def _analyze_assign(self, num):
        if num + 1 < self.length:
            new_num, node = self._analyze_expr(num + 1)
            if node is not None:
                self._variables.add(self.lex[num]['value'])
                return new_num, Assign(targets=[self._store_var(num)],
                                       value=node, **self._debug_details(num))
        return num + 1, None

    def _analyze_input(self, num):
        input_func = Call(func=Name(id='input', ctx=Load(), **self._debug_details(num)),
                          args=[], keywords=[], **self._debug_details(num))
        num += 1
        if num < self.length:
            lexeme = self.lex[num]
            if lexeme['lex'] == LEX['str']:
                if lexeme['value'].count(' '):
                    return num, None
            elif lexeme['lex'] != LEX['var']:
                return num, None
            else:
                input_func = Call(func=Name(id='int', ctx=Load(), **self._debug_details(num)),
                                  args=[input_func], keywords=[], **self._debug_details(num))
            self._variables.add(lexeme['value'])
            return num + 1, Assign(targets=[self._store_var(num)],
                                   value=input_func, **self._debug_details(num))
        return num, None

    def _analyze_if(self, num):
        if num + 1 >= self.length:
            return num + 1, None
        new_num, cond = self._analyze_expr(num + 1)
        if cond is not None and new_num < self.length:
            if self.lex[new_num]['lex'] == LEX['then']:
                new_num += 1
            if new_num < self.length:
                if self.lex[new_num]['lex'] == LEX['{']:
                    new_num, body = self._analyze_block(new_num)
                else:
                    new_num, body = self._analyze(new_num)
                    if body is not None:
                        body = [body]
                if body is not None:
                    orelse = None
                    if self.lex[new_num]['lex'] == LEX['else']:
                        new_num += 1
                        if new_num < self.length:
                            if self.lex[new_num]['lex'] == LEX['{']:
                                new_num, orelse = self._analyze_block(new_num)
                            else:
                                new_num, orelse = self._analyze(new_num)
                                if orelse is not None:
                                    orelse = [orelse]
                    if orelse is None:
                        orelse = []
                    return new_num, If(test=cond, body=body, orelse=orelse, **self._debug_details(num))
        raise ErrorHandler(ERROR, "If failed")

    def _analyze_print(self, num):
        if num + 1 >= self.length:
            return num + 1, None
        new_num, node = self._analyze_expr(num + 1)
        if node is not None:
            return new_num, Expr(value=Call(func=Name(id='print', ctx=Load()),
                                            args=[node], keywords=[]), **self._debug_details(num))
        return num + 1, None

    def _analyze_until(self, num):
        if num + 1 >= self.length:
            return num + 1, None
        new_num, cond = self._analyze_expr(num + 1)
        if cond is not None and new_num < self.length:
            if self.lex[new_num]['lex'] == LEX['then']:
                new_num += 1
            if new_num < self.length:
                if self.lex[new_num]['lex'] == LEX['{']:
                    new_num, body = self._analyze_block(new_num)
                else:
                    new_num, body = self._analyze(new_num)
                    if body is not None:
                        body = [body]
                if body is not None:
                    return new_num, While(test=UnaryOp(op=Not(), operand=cond, **self._debug_details(num + 1)),
                                          body=body, orelse=[], **self._debug_details(num))
        raise ErrorHandler(ERROR, "Misplaced jab tak")

    def _analyze_block(self, num):
        num += 1
        code = []
        while num < self.length:
            if self.lex[num]['lex'] == LEX['}']:
                return num + 1, code
            num, node = self._analyze(num)
            if node is not None:
                code.append(node)
        raise ErrorHandler(ERROR, "Missing '}'")

    def _analyze_e(self, num):
        lexeme = self.lex[num]
        if lexeme['lex'] == LEX['(']:
            if num + 1 >= self.length:
                return num + 1, None
            new_num, code = self._analyze_expr(num + 1)
            if self.lex[new_num]['lex'] != LEX[')']:
                raise ErrorHandler(ERROR, "Missing ')'")
            new_num += 1
            if new_num < self.length and self._is_not(new_num):
                new_num += 1
            if new_num < self.length and self.lex[new_num]['lex'] == LEX['hai']:
                new_num += 1
            return new_num, code
        if lexeme['lex'] == LEX['true']:
            k = 2 if (num + 1 < self.length and self.lex[num + 1]['lex'] == LEX['hai']) else 1
            return num + k, NameConstant(value=True, **self._debug_details(num))
        if lexeme['lex'] == LEX['false']:
            k = 2 if (num + 1 < self.length and self.lex[num + 1]['lex'] == LEX['hai']) else 1
            return num + k, NameConstant(value=False, **self._debug_details(num))
        if lexeme['lex'] == LEX['num']:
            k = 2 if (num + 1 < self.length and self.lex[num + 1]['lex'] == LEX['hai']) else 1
            return num + k, Num(n=int(lexeme['value']), **self._debug_details(num))
        if lexeme['lex'] == LEX['str']:
            k = 2 if (num + 1 < self.length and self.lex[num + 1]['lex'] == LEX['hai']) else 1
            return num + k, Str(s=lexeme['value'], **self._debug_details(num))
        if lexeme['lex'] == LEX['var']:
            if lexeme['value'] in self._variables:
                k = 2 if (num + 1 < self.length and self.lex[num + 1]['lex'] == LEX['hai']) else 1
                return num + k, Name(id=lexeme['value'], ctx=Load(), **self._debug_details(num))
            if num + 1 >= self.length:
                return num + 1, None
            return self._analyze_e(num + 1)
        raise ErrorHandler(ERROR, 'Unknown symbol')

    def _analyze_d(self, num):
        num, prev = self._analyze_e(num)
        if prev is None:
            raise ErrorHandler(ERROR)
        while num < self.length:
            lexeme = self.lex[num]
            if lexeme['lex'] == LEX['*']:
                op = Mult(**self._debug_details(num))
            elif lexeme['lex'] == LEX['/']:
                op = Div(**self._debug_details(num))
            elif lexeme['lex'] == LEX['%']:
                op = Mod(**self._debug_details(num))
            else:
                return num, prev
            num += 1
            if num >= self.length:
                raise ErrorHandler(ERROR, "Missing right operand")
            num, node = self._analyze_e(num)
            if node is None:
                raise ErrorHandler(ERROR)
            prev = BinOp(left=prev, op=op, right=node)
        return num, prev

    def _analyze_c(self, num):
        num, prev = self._analyze_d(num)
        if prev is None:
            raise ErrorHandler(ERROR)
        while num < self.length:
            lexeme = self.lex[num]
            if lexeme['lex'] == LEX['+']:
                op = Add(**self._debug_details(num))
            elif lexeme['lex'] == LEX['-']:
                op = Sub(**self._debug_details(num))
            else:
                return num, prev
            num += 1
            if num >= self.length:
                raise ErrorHandler(ERROR, "Missing right operand")
            num, node = self._analyze_d(num)
            if node is None:
                raise ErrorHandler(ERROR)
            prev = BinOp(left=prev, op=op, right=node)
        return num, prev

    def _analyze_b(self, num):
        lex_line = self.lex[num]['line']
        op = None
        num, prev = self._analyze_c(num)
        if prev is None:
            raise ErrorHandler(ERROR)
        if num >= self.length:
            return num, prev
        lexeme = self.lex[num]
        if lexeme['lex'] in (LEX['<'], LEX['>'], LEX['<='], LEX['>='], LEX['=='], LEX['!=']):
            if num + 1 >= self.length:
                return num + 1, prev
            new_num, node = self._analyze_c(num + 1)
            if node is None:
                return num + 1, prev
            if lexeme['lex'] == LEX['<']:
                op = Lt(**self._debug_details(num))
            elif lexeme['lex'] == LEX['>']:
                op = Gt(**self._debug_details(num))
            elif lexeme['lex'] == LEX['<=']:
                op = LtE(**self._debug_details(num))
            elif lexeme['lex'] == LEX['>=']:
                op = GtE(**self._debug_details(num))
            elif lexeme['lex'] == LEX['==']:
                op = Eq(**self._debug_details(num))
            elif lexeme['lex'] == LEX['!=']:
                op = NotEq(**self._debug_details(num))
            if lexeme['value'] == 'word':
                if lexeme['lex'] == LEX['>']:
                    op = Lt(**self._debug_details(num))
                elif lexeme['lex'] == LEX['<']:
                    op = Gt(**self._debug_details(num))
            op = Compare(left=prev, ops=[op], comparators=[node], **self._debug_details(num))
            if new_num + 1 < self.length and self.lex[new_num + 1]['lex'] == LEX['var'] and self.lex[new_num + 1][
                'value'] == 'nahi':
                new_num += 1
                op = UnaryOp(op=Not(), operand=op, **self._debug_details(new_num))
            if new_num < self.length and self.lex[new_num]['lex'] == LEX['hai']:
                new_num += 1
            return new_num, op
        elif lexeme['lex'] in (LEX['var'], LEX['('], LEX['str'], LEX['num']) and lexeme['line'] == lex_line:
            new_num, node = self._analyze_c(num)
            if new_num >= self.length:
                return new_num, prev
            lexeme = self.lex[new_num]
            if lexeme['value'] is None:
                raise ErrorHandler(ERROR, 'Misplaced relational operator')
            if lexeme['lex'] == LEX['<']:
                op = Lt(**self._debug_details(new_num))
            elif lexeme['lex'] == LEX['>']:
                op = Gt(**self._debug_details(new_num))
            elif lexeme['lex'] == LEX['<=']:
                op = LtE(**self._debug_details(new_num))
            elif lexeme['lex'] == LEX['>=']:
                op = GtE(**self._debug_details(new_num))
            elif lexeme['lex'] == LEX['==']:
                op = Eq(**self._debug_details(new_num))
            elif lexeme['lex'] == LEX['!=']:
                op = NotEq(**self._debug_details(new_num))
            op = Compare(left=prev, ops=[op], comparators=[node], **self._debug_details(num))
            if new_num + 1 < self.length and self.lex[new_num + 1]['lex'] == LEX['var'] and self.lex[new_num + 1][
                'value'] == 'nahi':
                new_num += 1
                op = UnaryOp(op=Not(), operand=op, **self._debug_details(new_num))
            if new_num + 1 < self.length and self.lex[new_num + 1]['lex'] == LEX['hai']:
                new_num += 1
            return new_num + 1, op
        else:
            return num, prev

    def _analyze_a(self, num):
        lex_num = num
        values = []
        num, node = self._analyze_b(num)
        if node is None:
            raise ErrorHandler(ERROR)
        values.append(node)
        while num < self.length:
            lexeme = self.lex[num]
            if lexeme['lex'] != LEX['&&']:
                break
            num += 1
            if num >= self.length:
                raise ErrorHandler(ERROR, 'Unexpected aur')
            num, node = self._analyze_b(num)
            if node is None:
                raise ErrorHandler(ERROR)
            values.append(node)
        if len(values) == 1:
            return num, values.pop()
        else:
            return num, BoolOp(op=And(**self._debug_details(lex_num)), values=values, **self._debug_details(lex_num))

    def _analyze_expr(self, num):
        """
        expr -> A ya expr | A
        A -> B A', A' -> aur B A' | e
        B -> C relational C N H | C C relational N H | C
        C -> D C', C' -> + D C' | - D C' | e
        D -> E D', D' -> * E D' | / E D' | % E D' | e
        E -> (expr) H | var H | num H | str H
        H -> e | hai
        N -> e | nahi
        """
        lex_num = num
        values = []
        num, node = self._analyze_a(num)
        if node is None:
            raise ErrorHandler(ERROR)
        values.append(node)
        while num < self.length:
            lexeme = self.lex[num]
            if lexeme['lex'] != LEX['||']:
                break
            num += 1
            if num >= self.length:
                raise ErrorHandler(ERROR, 'Unexpected aur')
            num, node = self._analyze_a(num)
            if node is None:
                raise ErrorHandler(ERROR)
            values.append(node)
        if len(values) == 1:
            return num, values.pop()
        else:
            return num, BoolOp(op=Or(**self._debug_details(lex_num)), values=values, **self._debug_details(lex_num))
