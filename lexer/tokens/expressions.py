from greencss.lexer.tokens.basic import identifier, pcall, number, unit, color, string, spaces, alpha
from greencss.lexer.tokens import Value, Variable, Color, Macro, Values, Expression, PseudoCall, String
from greencss.lexer.parsers.parsers import _, EOL, inf
from greencss.lexer.parsers.filters import join

varval = (_('$')/0 - identifier) / Variable.get

word = alpha * (1, inf) / join
value = (
        pcall          >> PseudoCall | 
        number - -unit >> Value      | 
        (color | word) >> Color      | 
        identifier     >> Value      | 
        string         >> String     | 
        varval
        )

expression_tail = spaces/0 - ['*/+-'] - spaces/0 - _('(').opt - spaces/0 - value - _(')').opt
expression = (_('(').opt - value - expression_tail * inf - _(')').opt) >> Expression

values = (
        (expression - ((_(',').opt - spaces)/0 - expression) * inf)
        ) >> Values
vallist = expression.commalist >> Values

cmacrocall = (
        _('%')/0 - identifier - (-(value.commalist).surround) - EOL
        ) / Macro.call

