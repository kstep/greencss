from greencss.lexer.parsers.parsers import _, A, inf, W
from greencss.lexer.tokens.charclasses import alpha, alnum, digit, hexdigit, space, delim
from greencss.lexer.parsers.filters import join
from greencss.lexer.parsers.compound import alter
from greencss.lexer.parsers.literals import lit

spaces = space * inf
delims = delim * inf
identifier = (alpha - alnum * inf) / join
flag = ('!' - _('not-').opt - alnum * (1, inf)) / join
flags = flag - (spaces/0 - flag) * inf

uinteger = digit * (1, inf) / join
integer = (_('-').opt - uinteger) / join
number = (integer - ('.' - uinteger).opt) / join

color_unit = (
        (digit * (1, 3) / join - _('%').opt)
            / (lambda c: int(c[0])*255//100 if len(c) > 1 else int(c[0]))
            == (lambda c: 0 <= c[0] <= 255)
        )
color_args = color_unit - (W(',')/0 - color_unit) * 2
color_hunit = (
        hexdigit * 2 / join
            / (lambda c: int(c[0], 16))
            == (lambda c: 0 <= c[0] <= 255)
        )
color = (
        (_('#')/'rgb' - color_hunit * 3) |
        ((_('rgb')|_('hls')|_('hsv')|_('yiq')) - _('(')/0 - color_args - _(')')/0)
        )
pcall = identifier - (A^space).braced / join
string = A.quoted

_units = ['em', 'ex', 'px', 'cm', 'mm', 'in', 'pt', 'pc', 'deg', 'rad'
          'grad', 'ms', 's', 'Hz', 'kHz', '%']
unit = _(alter(*map(lit, _units)))

