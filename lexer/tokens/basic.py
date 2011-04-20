from greencss.lexer.parsers.parsers import _, A, inf
from greencss.lexer.tokens.charclasses import alpha, alnum, digit, hexdigit, space, delim
from greencss.lexer.parsers.filters import join
from greencss.lexer.parsers.compound import alter
from greencss.lexer.parsers.literals import lit

spaces = space * inf
delims = delim * inf
identifier = (alpha - alnum * inf) / join

uinteger = digit * (1, inf) / join
integer = (_('-').opt - uinteger) / join
number = (integer - ('.' - uinteger).opt) / join

color = (_('#') - hexdigit * 6) / join
pcall = identifier - (A^space).braced / join
string = A.quoted

_units = ['em', 'ex', 'px', 'cm', 'mm', 'in', 'pt', 'pc', 'deg', 'rad'
          'grad', 'ms', 's', 'Hz', 'kHz', '%']
unit = _(alter(*map(lit, _units)))

