from lexer.parsers.helpers import wrap_parser

def rep(parser, min, max=None):
    '''
    Repeat from min to max times
    '''
    max = max or min
    @wrap_parser('rep', min, max)
    def wrapper(inp):
        tokens = []
        rest = inp
        for i in xrange(0, max):
            token, rest = parser(rest)
            if token is None:
                if i < min:
                    tokens = None
                    rest = inp
                break
            tokens.extend(token)

        return tokens, rest
    return wrapper

def seq(*parsers):
    '''
    Sequence of parsers
    '''
    @wrap_parser('seq', *parsers)
    def wrapper(inp):
        tokens = []
        rest = inp
        for p in parsers:
            token, rest = p(rest)
            if token is None:
                rest = inp
                tokens = None
                break
            tokens.extend(token)
        return tokens, rest
    wrapper.__name__ = 'seq(%s)' % ', '.join(map(lambda p: p.__name__, parsers))
    return wrapper

def alter(*parsers):
    '''
    One of parser
    '''
    @wrap_parser('alter', *parsers)
    def wrapper(inp):
        rest = inp
        token = None
        for p in parsers:
            token, rest = p(inp)
            if token is not None:
                break
        return token, rest
    return wrapper

def star(parser):
    '''
    Zero or more parser
    '''
    @wrap_parser('star', parser)
    def wrapper(inp):
        tokens = []
        rest = inp
        while True:
            token, rest = parser(rest)
            if token is None:
                break
            tokens.extend(token)
        return tokens, rest
    return wrapper

def plus(parser):
    '''
    One or more parser
    '''
    return wrap_parser('plus', parser)(seq(parser, star(parser)))

