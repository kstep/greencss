from greencss.lexer.tokens import Selector, Property, ComplexProperty, Variable, Macro, Rule, Arguments, IncludeFile, Metablock
from greencss.lexer.tokens.basic import identifier, spaces, digit, flag
from greencss.lexer.parsers.parsers import _, EOL, W, inf
from greencss.lexer.tokens.expressions import value, values, cmacrocall, vallist
from greencss.lexer.tokens.basic import string
from greencss.lexer.parsers.filters import join

vardef = identifier - W('=')/0 - value - EOL >> Variable

_cproperty = _(lambda inp: cproperty(inp))

cpholdr = _('&')
cid = ('#' - identifier) / join
cclass = ('.' - identifier) / join
cpclass = (':' - identifier) / join

sign = _(['+-'])
number = digit*(1,inf)
nthchild_arg = (
        sign.opt - number |
        sign.opt - number - 'n' - sign - number |
        'even' |
        'odd'
        ) / join
nthchild = (':nth-' - _('last-').opt - (_('child')|_('of-type')) - '(' - nthchild_arg - ')') / join

ctag = identifier | cpholdr
cmodifier = cid | cclass | cpclass | nthchild
catom = (
        (cmodifier * (1, inf)) | (ctag - cmodifier * inf)
        ) / join

cexpression_tail = spaces/' ' - (['+>'] - spaces/' ').opt - catom
cexpression = (catom - cexpression_tail*inf - spaces/0) / join

cselector = cexpression.commalist - _(':')/0 - EOL >> Selector
cproperty = (
        identifier - (':' - spaces)/0 - values - spaces/0 - flag.opt - EOL >> Property |
        (identifier - _('>')/0 - EOL -
            _cproperty.indent) / ComplexProperty |
        cmacrocall
        )

_crule = _(lambda inp: crule(inp))
crule = (
        cselector -
        ((cproperty | _crule).indent)
        ) >> Rule

cmacro = (
        W('@define').push()/0 - identifier -
            -(identifier.commalist.surround >> Arguments) -
        (_(':'))/0 - EOL -
        (cproperty | _crule).indent >> Macro
        ).drop()

cinclude = (
        W('@include')/0 - string - EOL
        ) / IncludeFile

cmetablock = (
        ('@' - identifier)/join - spaces/0 - vallist.opt - (spaces - ':')/0 - EOL -
            (crule * (1, inf)).indent
        ) >> Metablock

