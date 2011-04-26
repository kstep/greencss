
from greencss.lexer.parsers.parsers import inf
from greencss.lexer.parsers.helpers import clear_lines
from greencss.lexer.tokens.statements import vardef, cmacro, crule, cinclude, cmetablock, shebang
_parser = shebang.opt - (vardef/0 | cmacro/0 | cinclude | crule | cmetablock) * inf

def convert(data):
    data = clear_lines(data)
    token, rest = _parser(data)
    #print token, rest
    return ''.join(t.render() for t in token)

