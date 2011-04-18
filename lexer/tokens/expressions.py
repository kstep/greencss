from lexer.tokens.basic import identifier, pcall, number, unit, color, string, spaces, alpha
from lexer.tokens import Value, Variable, Color, Macro, Properties
from lexer.parsers.parsers import _, EOL, inf
from lexer.parsers.filters import join

varval = (_('$')/0 - identifier) / Variable.get
_expression = _(lambda inp: expression(inp))

word = alpha * (1, inf) / join
value = (
        pcall                   | 
        number - -unit >> Value | 
        (color | word) >> Color | 
        identifier              | 
        string                  | 
        varval
        )
values = (
        (_expression - ((_(',').opt - spaces)/0 - _expression) * inf)
        ) >> Properties
vallist = _expression.commalist

expression_tail = spaces/0 - ['*/+-'] - spaces/0 - _('(').opt - spaces/0 - value - _(')').opt
expression = _('(').opt/0 - value - expression_tail * inf - _(')').opt/0

cmacrocall = (
        _('%')/0 - identifier - (-(value.commalist).surround) - EOL
        ) / Macro.call

