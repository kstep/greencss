from lexer.parsers.tokens import Token
from lexer.parsers.state import state

class Value(Token):
    __slots__ = ('value', 'unit')
    def __str__(self):
        return '%s%s' % (self.value, self.unit)

class Selector(Token):
    def init(self, token):
        self.selector = token
    def __str__(self):
        return ', '.join(self.selector)

class Property(Token):
    __slots__ = ('name', 'value')
    def __str__(self):
        return '%s: %s' % (self.name, self.value)

class Variable(Token):
    variables = {}
    instance = None

    def init(self, token):
        self.__class__.variables[token[0]] = token[1]

    def __str__(self):
        return str(self.variables)

    @classmethod
    def get(cls, name):
        if state.stack and state.stack[-1].token and '@define' in state.stack[-1].token:
            return '$'+name[0]
        return cls.variables.get(name[0], '')

class Color(Token):
    __slots__ = ('color',)

class Macro(Token):
    macros = {}

    def init(self, token):

        self.name = token[0]
        if isinstance(token[1], Arguments):
            self.args, self.body = token[1].args, token[2:]
        else:
            self.args, self.body = [], token[1:]

        self.__class__.macros[self.name] = self

    def __str__(self):
        return '<%s(%s)[%s]>' % (self.name, ','.join(self.args), ';'.join(str(p) for p in self.body))

    @classmethod
    def call(cls, token):
        macro = cls.macros.get(token[0])

        if not macro:
            raise NameError('Macro \'%s\' is not defined' % token[0])

        if len(macro.args) != len(token)-1:
            raise TypeError('Macro %s requires exactly %d arguments (%d given)' % (macro.name,
                len(macro.args), len(token)-1))

        context = {}
        context.update(Variable.variables)
        if len(token) > 1:
            context.update(zip(macro.args, token[1:]))

        from copy import deepcopy as copy
        body = copy(macro.body)
        for prop in body:
            if isinstance(prop, Property):
                for i, val in enumerate(prop.value.properties):
                    if isinstance(val, basestring) and val.startswith('$'):
                        prop.value.properties[i] = context.get(val[1:], '')

        return body

class Rule(Token):
    def init(self, token):
        self.selector = token[0]
        self.properties = token[1:]

    def __str__(self):
        return '<%s{%s}>' % (self.selector, ';'.join(str(p) for p in self.properties))

class ComplexProperty(Token):
    __slots__ = ('properties',)
    def init(self, token):
        head, tail = token[0], token[1:]
        for t in tail:
            t.name = head + t.name
        self.properties = tail

    def __str__(self):
        return ';'.join(str(p) for p in self.properties)

class Arguments(Token):
    __slots__ = ('args',)
    def init(self, token):
        self.args = list(token)
    def __str__(self):
        return ', '.join(self.args)

class Properties(Token):
    __slots__ = ('properties',)
    def init(self, token):
        self.properties = list(token)
    
    def __str__(self):
        return ','.join(str(p) for p in self.properties)

