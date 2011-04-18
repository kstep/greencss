from lexer.parsers.helpers import wrap_parser

def pipe(parser, func):
    @wrap_parser('filter', func)
    def wrapper(inp):
        token, rest = parser(inp)
        if token is not None:
            token = func(token)
            if not isinstance(token, list):
                token = [token]
        return token, rest
    return wrapper

def join(token):
    return ''.join(token)

def check(parser, predicate):
    @wrap_parser('check', predicate)
    def wrapper(inp):
        token, rest = parser(inp)
        if token is not None and predicate(token):
            return token, rest
        return None, inp
    return wrapper

def take(parser, num):
    @wrap_parser('take', num)
    def wrapper(inp):
        token, rest = parser(inp)
        if token:
            token = [token[num]]
        return token, rest

