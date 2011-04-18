from lexer.parsers.helpers import wrap_parser
from lexer.parsers.compound import seq, alter, star
from lexer.parsers.literals import lit, charclass
from lexer.parsers.basic import anychar
from lexer.parsers.filters import join, pipe
from lexer.parsers.state import state
from lexer.parsers.indent import Indentation

def peek(parser):
    @wrap_parser('peek', parser)
    def wrapper(inp):
        token, rest = parser(inp)
        return token, inp
    return wrapper


def opt(parser):
    '''
    Parser is optional
    '''
    @wrap_parser('opt', parser)
    def wrapper(inp):
        token, rest = parser(inp)
        return token or [], rest
    return wrapper

def skip(parser):
    '''
    Skip this parser
    '''
    @wrap_parser('skip', parser)
    def wrapper(inp):
        _, rest = parser(inp)
        return _ and [], rest
    return wrapper

def but(parser):
    '''
    Invert parser
    '''
    def wrapper(inp):
        token, rest = parser(inp)
        return [] if token is None else None, inp
    return wrapper

def commalist(parser, comma=lit(','), wsp=charclass('\t ')):
    delim = seq(star(wsp), comma, star(wsp))
    return wrap_parser('commalist')(
            seq(parser, star(seq(skip(delim), parser))))


def surround(parser, left=lit('('), right=lit(')')):
    return wrap_parser('surround')(
            seq(skip(left), parser, skip(right)))

def braced(char=anychar, left=lit('('), right=lit(')'), esc=lit('\\')):
    charseq = seq(but(right), char)
    if esc:
        escseq = seq(skip(esc), alter(right, esc))
        charseq = alter(escseq, charseq)
    return wrap_parser('braced')(
                surround(pipe(star(charseq), join), left, right)
                )

def quoted(char=anychar, quot=charclass('\'"'), esc=lit('\\')):
    charseq = seq(but(state.check), char)
    if esc:
        escseq = seq(skip(esc), alter(quot, esc))
        charseq = alter(escseq, charseq)
    return wrap_parser('quoted')(
                surround(pipe(star(charseq), join), state.push(quot), state.pop)
                )

def indent(line):
    indent = skip(Indentation(True))
    dedent = skip(Indentation(False))
    keep = skip(Indentation(None))
    return seq(indent, opt(line), star(seq(keep, line)), peek(dedent))

