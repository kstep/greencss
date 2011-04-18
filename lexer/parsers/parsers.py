
__all__ = ['_', 'T', 'F', 'A', 'W', 'EOL', 'EOF', 'inf']

import lexer.parsers.compound as compound
import lexer.parsers.literals as literals
import lexer.parsers.filters as filters
import lexer.parsers.state as state
import lexer.parsers.basic as basic
import lexer.parsers.tools as tools
from lexer.parsers.indent import Indentation

# Infinity
inf = float('inf')
function = type(lambda: None)

class Parser(object):
    def __init__(self, parser=basic.anychar):
        self.parser = parser

    def __call__(self, inp):
        return self.parser(inp)

    def __or__(self, other):
        '''
        Either self or other matches
        '''
        parser = compound.alter(self.parser, _(other).parser)
        return Parser(parser)

    def __ror__(self, other):
        parser = compound.alter(_(other).parser, self.parser)
        return Parser(parser)

    def __sub__(self, other):
        '''
        Match self, then match other
        '''
        parser = compound.seq(self.parser, _(other).parser)
        return Parser(parser)

    def __rsub__(self, other):
        parser = compound.seq(_(other).parser, self.parser)
        return Parser(parser)

    def __div__(self, other):
        '''
        Filter matched with self through other function
        '''
        if not other:
            parser = tools.skip(self.parser)
        else:
            parser = filters.pipe(self.parser, other)
        return Parser(parser)

    def __neg__(self):
        '''
        Self if optional
        '''
        parser = tools.opt(self.parser)
        return Parser(parser)

    def __mul__(self, other):
        '''
        Repeat self other times (num of (min, max))
        '''
        if isinstance(other, tuple):
            min, max = other
        else:
            min, max = None, other

        parser = basic.fail

        if max == inf:
            if min is None:
                min = 0
            if min == 0:
                parser = compound.star(self.parser)
            elif min == 1:
                parser = compound.plus(self.parser)
            elif min > 1:
                parser = compound.seq(
                        compound.rep(self.parser, min),
                        compound.star(self.parser))
        else:
            if min is None:
                min = max
            elif min > max:
                min, max = max, min
            if min > -1 and max > 0:
                parser = compound.rep(self.parser, min, max)
        return Parser(parser)
    
    def __invert__(self):
        '''
        Don't match self
        '''
        parser = tools.but(self.parser)
        return Parser(parser)

    def __xor__(self, other):
        '''
        Match self, but not after other
        '''
        parser = compound.seq(tools.but(_(other).parser), self.parser)
        return Parser(parser)

    def __rxor__(self, other):
        parser = compound.seq(tools.but(self.parser), _(other).parser)
        return Parser(parser)

    def __and__(self, other):
        '''
        Match self only if other function permits so
        '''
        parser = filters.check(self.parser, other)
        return Parser(parser)

    def __rshift__(self, other):
        '''
        Wrap self into other (or compose self with other)
        '''
        parser = other(self.parser)
        return Parser(parser)

    def push(self):
        '''
        Push matched state
        '''
        return Parser(state.state.push(self.parser))

    def st(self):
        '''
        Check last saved state
        '''
        return Parser(compound.seq(self.parser, state.state.check))

    def pop(self):
        '''
        Pop last saved state and check it
        '''
        return Parser(compound.seq(self.parser, state.state.pop))

    def drop(self):
        '''
        Drop last saved state, no check
        '''
        return Parser(compound.seq(self.parser, state.state.drop))

    def __getattr__(self, name):
        '''
        Apply any compound combinator
        '''
        parser = basic.fail
        combinator = getattr(tools, name, None)
        if combinator:
            parser = combinator(self.parser)
        return Parser(parser)

# Match string or char range
_ = lambda word: word if isinstance(word, Parser) else Parser(
        literals.lit(word) if isinstance(word, basestring) else
        literals.charrange(*word) if isinstance(word, (list, tuple)) else
        word)

# Match any character
A = Parser(basic.anychar)

# Match word (omit word bounds)
W = lambda word: Parser(literals.word(word))

# True and false
T = Parser(basic.success)
F = Parser(basic.fail)

# End of file parser
EOF = Parser(basic.end_of_inp)
# End of line parser
EOL = Parser(basic.end_of_line)

indent = _(Indentation(True))
dedent = _(Indentation(False))
keep = _(Indentation(None))

