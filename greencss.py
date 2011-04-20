
from lexer.parsers.parsers import inf
from lexer.parsers.helpers import clear_lines
from lexer.tokens.statements import vardef, cmacro, crule
_parser = (vardef/0 | cmacro/0 | crule) * inf

def convert(data):
    token, rest = _parser(clear_lines(data))
    return ''.join(t.render() for t in token)

