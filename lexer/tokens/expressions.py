from greencss.lexer.tokens.basic import identifier, pcall, number, unit, color, string, spaces, alpha
from greencss.lexer.tokens import Variable, Macro, Values, Expression, PseudoCall, MethodCall
from greencss.lexer.tokens import Value, Color, String
from greencss.lexer.parsers.parsers import _, EOL, inf
from greencss.lexer.parsers.filters import join

varval = (_('$')/0 - identifier) / Variable.get

_vallist = _(lambda inp: vallist(inp))
mcall = _('.')/0 - identifier - (_('(')/0 - (spaces/0 - _vallist).opt - _(')')/0)
word = alpha * (1, inf) / join
value = ((
        number - unit.opt >> Value      | 
        string            >> String     | 
        (color | word)    >> Color      | 
        pcall             >> PseudoCall | 
        identifier        >> Value      | 
        varval
        ) - mcall.opt) / MethodCall

expression_tail = spaces/0 - ['*/+-'] - spaces/0 - (_('(')< spaces/0 - value >_(')'))
expression = (
        _('(')< value - expression_tail * inf >_(')')
            #== (lambda t: t.count('(') == t.count(')'))
        ) >> Expression

values = (
        (expression - ((_(',').opt - spaces)/0 - expression) * inf)
        ) >> Values
vallist = expression.commalist >> Values

cmacrocall = (
        _('%')/0 - identifier - (-(value.commalist).surround) - EOL
        ) / Macro.call

