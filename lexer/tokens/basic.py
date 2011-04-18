from lexer.parsers.parsers import _, A, inf
from lexer.tokens.charclasses import alpha, alnum, digit, hexdigit, space, delim
from lexer.parsers.filters import join

spaces = space * inf
delims = delim * inf
identifier = (alpha - alnum * inf) / join
number = (
        _('-').opt - digit * (1, inf) -
        (_('.') - digit * (1, inf)).opt
        ) / join
color = (_('#') - hexdigit * 6) / join
pcall = (identifier - (A^space).braced) / join
string = A.quoted

_units = ['em', 'ex', 'px', 'cm', 'mm', 'in', 'pt', 'pc', 'deg', 'rad'
          'grad', 'ms', 's', 'Hz', 'kHz', '%']
unit = reduce(lambda a, i: a | i, map(_, _units))

