from lexer.tokens import Selector, Property, ComplexProperty, Variable, Macro, Rule, Arguments
from lexer.tokens.basic import identifier, spaces
from lexer.parsers.parsers import _, EOL, W, inf
from lexer.tokens.expressions import value, values, cmacrocall
from lexer.parsers.filters import join

vardef = identifier - W('=')/0 - value - EOL >> Variable

_cproperty = _(lambda inp: cproperty(inp))

cpholdr = _('&')
cid = ('#' - identifier) / join
cclass = ('.' - identifier) / join
cpclass = (':' - identifier) / join

ctag = identifier | cpholdr
cmodifier = cid | cclass | cpclass
catom = (
        (cmodifier * (1, inf)) | (ctag - cmodifier * inf)
        ) / join

cexpression_tail = spaces/0 - ([',+>'] - spaces/0).opt - catom
cexpression = catom - cexpression_tail*inf - spaces/0


cselector = cexpression - _(':')/0 - EOL >> Selector
cproperty = (
        identifier - (':' - spaces)/0 - values - EOL >> Property |
        identifier - _('>')/0 - EOL -
            (_cproperty.indent)
            >> ComplexProperty |
        cmacrocall
        )

cmacro = (
        (W('@define').push()/0 - identifier -
            -(identifier.commalist.surround >> Arguments) -
        (_(':'))/0 - EOL -
        (cproperty.indent)
        ) >> Macro).drop()

_crule = _(lambda inp: crule(inp))
crule = (
        cselector -
        ((cproperty | _crule).indent)
        ) >> Rule

