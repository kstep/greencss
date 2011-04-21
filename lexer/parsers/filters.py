from greencss.lexer.parsers.helpers import wrap_parser

def pipe(parser, func):
    @wrap_parser('pipe', func)
    def wrapper(inp):
        token, rest = parser(inp)
        if token is not None:
            token = func(token)
            if token is None:
                rest = inp
            elif not isinstance(token, list):
                token = [token]
        return token, rest
    return wrapper

def join(token):
    return ''.join(token)

def repl(string):
    def wrapper(token):
        return string
    return wrapper

def check(predicate):
    def wrapper(token):
        return token if predicate(token) else None
    return wrapper

def take(num):
    def wrapper(token):
        return token[num]
    return wrapper
