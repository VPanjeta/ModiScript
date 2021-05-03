from .utils import LEX, ErrorHandler, ERROR, CONGRESS_RULE, STARTING_TROUBLE, MISQUOTE, WORDS
import re
import sys

mitrooon = re.compile(r'^mith?roo?o?n?$')
acche = re.compile(r'^ac[ch]?hee?$')
barabar = re.compile(r'^bara+bar$')
sach = re.compile(r'^sac[ch]?h$')
jhoot = re.compile(r'^jh?(oo|u)t$')


class Lexer:
    def __init__(self, value, value_type="filename"):
        self.contents = []
        if value_type == "filename":
            with open(value) as f:
                self.contents = list(map(lambda x: x.lower(), f.readlines()))
        else:
            self.contents = value.lower().split("\n")
        self.stack = []
        self.clear = False

    @staticmethod
    def lexeme(lex, value=None, line=0, offset=0):
        return locals()

    @staticmethod
    def normalize(word):
        if word in WORDS:
            word = WORDS[word]
        elif mitrooon.search(word):
            word = 'mitrooon'
        elif acche.search(word):
            word = 'acche'
        elif barabar.search(word):
            word = 'barabar'
        elif sach.search(word):
            word = 'sach'
        elif jhoot.search(word):
            word = 'jhoot'
        return word

    def _push(self, *lex):
        self.stack.append(lex)
        self.clear = True

    def on_top(self, *lex):
        i = len(self.stack) - 1
        for l in lex[::-1]:
            if i < 0 or self.stack[i][:2] != l:
                return False
            i -= 1
        return True

    def pop(self):
        if self.stack:
            return self.stack.pop()
        raise ErrorHandler(ERROR, 'Empty pop')

    @staticmethod
    def _is_var(lex, value):
        return lex['lex'] == LEX['var'] and lex['value'] == value

    def analyze(self):
        lexer = self._analyze_lexemes()
        lex = next(lexer)
        if not Lexer._is_var(lex, 'mitrooon'):
            raise ErrorHandler(STARTING_TROUBLE)
        lexemes = list(lexer)
        end = 'acche din aa gaye'.split()
        try:
            while end:
                if not Lexer._is_var(lexemes.pop(), end.pop()):
                    raise ErrorHandler(CONGRESS_RULE)
        except IndexError:
            raise ErrorHandler(CONGRESS_RULE)
        return lexemes

    def _analyze_lexemes(self):
        """
        Identify lexemes and return tokens.
        """
        num = 0
        self.stack = []
        self.clear = False
        for line in self.contents:
            num += 1
            offset = 0
            length = len(line)
            while offset < length:
                token = line[offset]
                if self.clear:
                    for lex in self.stack:
                        yield Lexer.lexeme(*lex)
                    self.stack = []
                    self.clear = False
                elif token.isspace():
                    offset += 1
                elif line[offset: offset + 2] in ('==', '&&', '||', '<=', '>=', '!='):
                    self._push(LEX[line[offset: offset + 2]], None, num, offset)
                    offset += 2
                elif token in '+-*/%(){}=<>!':
                    self._push(LEX[token], None, num, offset)
                    offset += 1
                elif token.isdigit():
                    n = ''
                    o = offset
                    while o < length and line[o].isdigit():
                        n += line[o]
                        o += 1
                    self._push(LEX['num'], int(n), num, offset)
                    offset = o
                elif token.isalpha():
                    w = ''
                    o = offset
                    while o < length and line[o].isalpha():
                        w += line[o]
                        o += 1
                    w = Lexer.normalize(w)
                    if w == 'agar':
                        self._push(LEX['if'], None, num, offset)
                    elif w == 'toh' and self.on_top((LEX['var'], 'nahi')):
                        _, _, lex_line, lex_offset = self.pop()
                        self._push(LEX['else'], None, lex_line, lex_offset)
                    elif w == 'toh':
                        self._push(LEX['then'], None, num, offset)
                    elif w == 'tak' and self.on_top((LEX['var'], 'jab')):
                        _, _, lex_line, lex_offset = self.pop()
                        self._push(LEX['until'], None, lex_line, lex_offset)
                    elif w == 'behno' and self.on_top((LEX['var'], 'bhaiyo'), (LEX['&&'], None)):
                        self.pop()
                        _, _, lex_line, lex_offset = self.pop()
                        self._push(LEX['print'], None, lex_line, lex_offset)
                    elif w == 'baat' and self.on_top((LEX['var'], 'mann'), (LEX['var'], 'ki')):
                        self.pop()
                        _, _, lex_line, lex_offset = self.pop()
                        self._push(LEX['input'], None, lex_line, lex_offset)
                    elif w == 'plus':
                        self._push(LEX['+'], None, num, offset)
                    elif w == 'substract':
                        self._push(LEX['-'], None, num, offset)
                    elif w == 'taimes':
                        self._push(LEX['*'], None, num, offset)
                    elif w == 'break':
                        self._push(LEX['/'], None, num, offset)
                    elif w == 'modi':
                        self._push(LEX['%'], None, num, offset)
                    elif w == 'kam':
                        self._push(LEX['<'], 'word', num, offset)
                    elif w == 'zyada':
                        self._push(LEX['>'], 'word', num, offset)
                    elif w == 'barabar':
                        self._push(LEX['=='], 'word', num, offset)
                    elif w == 'aur':
                        self._push(LEX['&&'], None, num, offset)
                        self.clear = False
                    elif w == 'ya':
                        self._push(LEX['||'], None, num, offset)
                    elif w == 'hai':
                        self._push(LEX['hai'], None, num, offset)
                    elif w == 'se':
                        pass
                    elif w == 'sach':
                        self._push(LEX['true'], None, num, offset)
                    elif w == 'jhoot':
                        self._push(LEX['false'], None, num, offset)
                    else:
                        self._push(LEX['var'], w, num, offset)
                        self.clear = False
                    offset = o
                elif token == '"' or token == "'":
                    w = ''
                    o = offset + 1
                    while o < length and line[o] != token:
                        if line[o] == '\\':
                            o += 1
                        w += line[o]
                        o += 1
                    if o == length:
                        raise ErrorHandler(MISQUOTE, line)
                    self._push(LEX['str'], w, num, offset)
                    offset = o + 1
                else:
                    self._push(LEX['sym'], num, offset)
                    offset += 1
        for lex in self.stack:
            yield Lexer.lexeme(*lex)
        self.stack = []
        self.clear = False
        if sys.version_info >= (3, 7):
            return
        raise StopIteration()
