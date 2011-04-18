
def wrap_parser(myname, *args):
    def decorator(func):
        name = '%s(%s)' % (myname, ', '.join(map(lambda a: str(getattr(a, '__name__', a)), args)))
        func.__name__ = name
        return func
    return decorator

def clear_lines(inp):
    return '\n'.join(filter(lambda l: len(l) > 0, map(lambda l: l.rstrip(), inp.strip().splitlines())))
