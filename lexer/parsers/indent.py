
from lexer.parsers.compound import plus
from lexer.parsers.literals import charclass

class Indentation(object):

    class Indent:
        pass
    class Dedent:
        pass

    stack = [0]
    spaces = staticmethod(plus(charclass(' \t')))

    def __init__(self, indent=None):
        self.__name__ = 'indent' if indent else 'dedent'
        self.indent = indent

    def __call__(self, inp):
        result = None
        token, rest = self.spaces(inp)
        if token is None:
            token = []

        token = ''.join(token).expandtabs()
        level = len(token)
        try:
            slevel = self.stack[-1]
        except IndexError:
            self.__class__.stack.append(0)
            slevel = 0

        if level == slevel:
            indent = None
            result = []
        elif level > slevel:
            indent = True
            result = [self.Indent]
        elif level < slevel:
            indent = False
            result = [self.Dedent]

        if self.indent is not indent:
            result = None
            rest = inp
        elif indent is not None:
            if indent:
                self.__class__.stack.append(level)
            else:
                self.__class__.stack.pop()

        #import lexer.parsers.basic as basic
        #print self.indent, self.stack, result, level, basic.lastline
        return result, rest

