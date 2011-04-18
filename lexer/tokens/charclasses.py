__all__ = ['space', 'delim', 'alpha', 'alnum', 'digit', 'hexdigit']

from lexer.parsers.parsers import _
delim = _([' \t\n\r'])
space = _([' \t'])
alpha = _(['A','Z', 'a','z', '_-'])
alnum = _(['A','Z', 'a','z', '0','9', '_-'])
digit = _(['0','9'])
hexdigit = _(['0','9', 'A','F', 'a','f'])
