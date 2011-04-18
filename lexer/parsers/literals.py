
from lexer.parsers.helpers import wrap_parser

def lit(w):
    @wrap_parser('lit', w)
    def wrapper(inp):
        if not inp.startswith(w):
            return None, inp
        return [w], inp[len(w):]
    return wrapper


def charclass(chars):
    @wrap_parser('charclass', len(chars))
    def wrapper(inp):
        token = None
        rest = inp
        try:
            for c in chars:
                if inp[0] == c:
                    token = [c]
                    rest = inp[1:]
                    break
        except IndexError:
            pass
        return token, rest
    return wrapper

def charrange(*limits):
    chars = ''
    limits = list(limits)
    if len(limits) % 2 != 0:
        chars = limits.pop()
    chars = ''.join(
            ''.join(map(unichr, xrange(ord(limits[i]), ord(limits[i+1])+1)))
                for i in xrange(0, len(limits), 2)
                ) + chars
    return charclass(chars)

def regexp(rex):
    import re
    rex = re.compile(rex)
    @wrap_parser('regexp', rex)
    def wrapper(inp):
        rest = inp
        token = rex.match(rest)
        if token:
            token = [token.group(0)]
            rest = rex.sub('', inp)
        return token, rest
    return wrapper

def word(w, border='\t '):
    from lexer.parsers.compound import seq, star
    border = star(charclass(border))
    return wrap_parser('word', w)(
            seq(border, lit(w), border)
            )

