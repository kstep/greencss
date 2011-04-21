
__all__ = ['_', 'T', 'F', 'A', 'W', 'EOL', 'EOF', 'inf']

import greencss.lexer.parsers.compound as compound
import greencss.lexer.parsers.literals as literals
import greencss.lexer.parsers.filters as filters
import greencss.lexer.parsers.state as state
import greencss.lexer.parsers.basic as basic
import greencss.lexer.parsers.tools as tools
from greencss.lexer.parsers.indent import Indentation

# Infinity
inf = float('inf')
function = type(lambda: None)

class Parser(object):
    '''
    This class defines syntax for parser building by wrapping different underlying functional parsers.

    A - B - C
        A, followed by B and then C

    A | B | C
        either A, B or C, whatever matches first

    L < A > R
        A is surrounded by balanced pair of optional L and R

    A / F
        A replaced by F (filter function, zero or string)

    A >> B
        A wrapped into B (function or class)

    A ^ B
        A, but not after B, i.e. exclude B from A

    A & D
        A parser is decorated with D (function)

    -A
        A is optional, i.e. match zero to one A

    ~A
        don't match A

    A * N
        repeat A exactly N times, if N is inf, then repeat from 0 to infinity

    A * (N, M)
        repeat A from N to M times, N < M

    A == P
    A != P
        match A only if matched token passes (or not) test by predicate P

    A.T
        apply tool T to A (see lexer.parser.tools for details)

    A[I]
        get Ith token from matched tokens

    A[N:M]
        get tokens from Nth up to Mth

    A.push([checker]), A.st(), A.pop(), A.drop()
        operations on state stack:
            * A.push() - match and push token into stack,
            * A.st() - match and check against top stacked token for equality, stack is unchanged,
            * A.pop() - pop top stacked token, match and check against popped token,
            * A.drop() - match unconditionally, then just drop top stacked token.
        A.push() accepts optional checker function to test popped value against just matched one,
        defaults to equality function.

    A(input)
        Run parser for given input (must be a string), returns a pair of matched tokens and the rest
        unparsed part of string. If parser totally failed to parse input string, then the result will be
        None, otherwise it will be a list of matched tokens (empty list is possible, but it only means all
        tokens are swallowed by parser and doesn't mean it failed). If parser succeed to parse the whole
        string, then the rest part will be empty string.
    '''

    args_stack = []
    state_stack = []
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
            if isinstance(other, basestring):
                parser = filters.pipe(self.parser, filters.repl(other))
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
                if min == 0 and max == 1:
                    parser = tools.opt(self.parser)
                else:
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
        parser = other(self.parser)
        return Parser(parser)

    def _checker(self, func):
        if isinstance(func, basestring):
            checker = lambda token: token[0] == func
        elif isinstance(func, tuple):
            checker = lambda token: token == func
        else:
            checker = filters.check(func)
        return checker

    def __eq__(self, func):
        '''
        Match self only if other function permits so
        '''
        checker = self._checker(func)
        parser = filters.pipe(self.parser, checker)
        return Parser(parser)

    def __ne__(self, func):
        checker = self._checker(func)
        parser = filters.pipe(self.parser, lambda token: not checker(token))
        return Parser(parser)

    def __rshift__(self, other):
        '''
        Wrap self into other (or compose self with other)
        '''
        from greencss.lexer.parsers.tokens import TokenError
        def filter(token):
            try:
                return other(*token)
            except TokenError:
                return None
        parser = filters.pipe(self.parser, filter)
        return Parser(parser)

    def __lt__(self, other):
        other.args_stack.append(self)
        return other

    def __gt__(self, other):
        '''
        Self is enclosed into balanced pair of parsers:
            left <( parser )> right
        Both side parsers are considered optional automatically,
        as this parser doesn't have sense for non-optional border
        parsers, use (left - parser - right) syntax for arbitrary
        borders.
        '''
        left, right = self.args_stack.pop(), other

        def left_parser(inp):
            token, rest = left(inp)
            if token is None:
                return [], inp
            self.state_stack.append(token)
            return token, rest

        def right_parser(inp):
            token, rest = right(inp)
            if token is None:
                return [], inp
            try:
                self.state_stack.pop()
            except IndexError:
                return [], inp
            return token, rest

        parser = compound.seq(left_parser, self.parser, right_parser)
        return Parser(parser)

    def push(self, checker=(lambda s, t: s == t)):
        '''
        Push matched state
        '''
        return Parser(state.state.push(self.parser, checker))

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

    def __getitem__(self, index):
        parser = filters.pipe(self.parser, filters.take(index))
        return Parser(parser)

    def __getslice__(self, first, last):
        parser = filters.pipe(self.parser, lambda t: t[first:last])
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

