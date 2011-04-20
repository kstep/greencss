
from lexer.parsers.parsers import inf
from lexer.parsers.helpers import clear_lines
from lexer.tokens.statements import vardef, cmacro, crule
_parser = (vardef/0 | cmacro/0 | crule) * inf

def convert(data):
    data = clear_lines(data)
    token, rest = _parser(data)
    #print token, rest
    return ''.join(t.render() for t in token)

