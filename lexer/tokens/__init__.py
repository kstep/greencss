from lexer.parsers.tokens import Token, TokenError
from lexer.parsers.state import state
from itertools import product

class Unit(object):
    _conv = {
        'scale': {
            'em': 1.0,
            'ex': 1.8,
            '%' : 100.0
        },
        'length': {
            'mm': 1.0,
            'cm': 10.0,
            'in': 25.4,
            'pt': 25.4 / 72,
            'pc': 25.4 / 6
        },
        'time': {
            'ms': 1.0,
            's' : 1000.0
        },
        'freq': {
            'Hz' : 1.0,
            'kHz': 1000.0
        }
    }
    _conv_mapping = {}
    for t, m in _conv.iteritems():
        for k in m:
            _conv_mapping[k] = t

    @classmethod
    def convert(cls, val1, val2):
        if val1.unit == val2.unit:
            return val1, val2

        if not (val1.unit and val2.unit):
            if val1.unit:
                val2.unit = val1.unit
            else:
                val1.unit = val2.unit
            return val1, val2

        try:
            table1 = cls._conv_mapping[val1.unit]
        except KeyError:
            raise ArithmeticError('Type \'%s\' is unconvertible' % (val1.unit))

        try:
            table2 = cls._conv_mapping[val2.unit]
        except KeyError:
            raise ArithmeticError('Type \'%s\' is unconvertible' % (val2.unit))

        if table1 != table2:
            raise ArithmeticError('Types \'%s\' and \'%s\' are incompatible' % (val1.unit, val2.unit))

        koeff1 = cls._conv[table1][val1.unit]
        koeff2 = cls._conv[table2][val2.unit]
        val = Value()
        val.value, val.unit = (float(val1) / koeff2 * koeff1, val2.unit)
        return val, val2

    @classmethod
    def coerce(cls, meth):
        def wrapper(self, other):
            b, a = cls.convert(other, self)
            result = Value()
            result.value = meth(a, b)
            result.unit = a.unit
            return result
        return wrapper

class PseudoCall(Token):
    __slots__ = ('name', 'args')
    def init(self, token):
        self.name, self.args = token[0], token[1]

    def render(self, context={}):
        return '%s(%s)' % (self.name, self.args)

class String(Token):
    __slots__ = ('value',)

    def render(self, context={}):
        if " " in self.value:
            return '"' + self.value + '"'
        else:
            return self.value

class Value(Token):
    __slots__ = ('value', 'unit')

    def render(self, context={}):
        return '%s%s' % (self.value, self.unit)

    @Unit.coerce
    def __add__(self, other):
        return float(self) + float(other)
    __radd__ = __add__

    @Unit.coerce
    def __mul__(self, other):
        return float(self) * float(other)
    __rmul__ = __mul__

    @Unit.coerce
    def __rdiv__(self, other):
        return float(self) / float(other)

    @Unit.coerce
    def __div__(self, other):
        return float(other) / float(self)

    @Unit.coerce
    def __rmod__(self, other):
        return int(self) % int(other)

    @Unit.coerce
    def __mod__(self, other):
        return int(other) % int(self)

    @Unit.coerce
    def __sub__(self, other):
        return float(other) - float(self)

    @Unit.coerce
    def __rsub__(self, other):
        return float(self) - float(other)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

class Selector(Token):
    def init(self, token):
        self.values = token

    @staticmethod
    def inherit(pair):
        base, s = pair
        return (s.replace('&', base) if '&' in s else base + ' ' + s).strip()

    def render(self, context={}):
        base = context.get('&', [''])
        return ', '.join(map(self.inherit, product(base, self.values)))

class Property(Token):
    __slots__ = ('name', 'value')
    def render(self, context={}):
        return '%s: %s;' % (self.name, self.value.render(context))

class Variable(Token):
    variables = {}
    instance = None

    def init(self, token):
        self.__class__.variables[token[0]] = token[1]

    def render(self, context={}):
        return str(self.variables)

    @classmethod
    def get(cls, name):
        if state.stack and state.stack[-1].token and '@define' in state.stack[-1].token:
            return '$'+name[0]
        return cls.variables.get(name[0], '')

class Color(Value):
    __slots__ = ('value',)
    _names = {
        'aliceblue'            : '#f0f8ff',
        'antiquewhite'         : '#faebd7',
        'aqua'                 : '#00ffff',
        'aquamarine'           : '#7fffd4',
        'azure'                : '#f0ffff',
        'beige'                : '#f5f5dc',
        'bisque'               : '#ffe4c4',
        'black'                : '#000000',
        'blanchedalmond'       : '#ffebcd',
        'blue'                 : '#0000ff',
        'blueviolet'           : '#8a2be2',
        'brown'                : '#a52a2a',
        'burlywood'            : '#deb887',
        'cadetblue'            : '#5f9ea0',
        'chartreuse'           : '#7fff00',
        'chocolate'            : '#d2691e',
        'coral'                : '#ff7f50',
        'cornflowerblue'       : '#6495ed',
        'cornsilk'             : '#fff8dc',
        'crimson'              : '#dc143c',
        'cyan'                 : '#00ffff',
        'darkblue'             : '#00008b',
        'darkcyan'             : '#008b8b',
        'darkgoldenrod'        : '#b8860b',
        'darkgray'             : '#a9a9a9',
        'darkgreen'            : '#006400',
        'darkkhaki'            : '#bdb76b',
        'darkmagenta'          : '#8b008b',
        'darkolivegreen'       : '#556b2f',
        'darkorange'           : '#ff8c00',
        'darkorchid'           : '#9932cc',
        'darkred'              : '#8b0000',
        'darksalmon'           : '#e9967a',
        'darkseagreen'         : '#8fbc8f',
        'darkslateblue'        : '#483d8b',
        'darkslategray'        : '#2f4f4f',
        'darkturquoise'        : '#00ced1',
        'darkviolet'           : '#9400d3',
        'deeppink'             : '#ff1493',
        'deepskyblue'          : '#00bfff',
        'dimgray'              : '#696969',
        'dodgerblue'           : '#1e90ff',
        'firebrick'            : '#b22222',
        'floralwhite'          : '#fffaf0',
        'forestgreen'          : '#228b22',
        'fuchsia'              : '#ff00ff',
        'gainsboro'            : '#dcdcdc',
        'ghostwhite'           : '#f8f8ff',
        'gold'                 : '#ffd700',
        'goldenrod'            : '#daa520',
        'gray'                 : '#808080',
        'green'                : '#008000',
        'greenyellow'          : '#adff2f',
        'honeydew'             : '#f0fff0',
        'hotpink'              : '#ff69b4',
        'indianred'            : '#cd5c5c',
        'indigo'               : '#4b0082',
        'ivory'                : '#fffff0',
        'khaki'                : '#f0e68c',
        'lavender'             : '#e6e6fa',
        'lavenderblush'        : '#fff0f5',
        'lawngreen'            : '#7cfc00',
        'lemonchiffon'         : '#fffacd',
        'lightblue'            : '#add8e6',
        'lightcoral'           : '#f08080',
        'lightcyan'            : '#e0ffff',
        'lightgoldenrodyellow' : '#fafad2',
        'lightgreen'           : '#90ee90',
        'lightgrey'            : '#d3d3d3',
        'lightpink'            : '#ffb6c1',
        'lightsalmon'          : '#ffa07a',
        'lightseagreen'        : '#20b2aa',
        'lightskyblue'         : '#87cefa',
        'lightslategray'       : '#778899',
        'lightsteelblue'       : '#b0c4de',
        'lightyellow'          : '#ffffe0',
        'lime'                 : '#00ff00',
        'limegreen'            : '#32cd32',
        'linen'                : '#faf0e6',
        'magenta'              : '#ff00ff',
        'maroon'               : '#800000',
        'mediumaquamarine'     : '#66cdaa',
        'mediumblue'           : '#0000cd',
        'mediumorchid'         : '#ba55d3',
        'mediumpurple'         : '#9370db',
        'mediumseagreen'       : '#3cb371',
        'mediumslateblue'      : '#7b68ee',
        'mediumspringgreen'    : '#00fa9a',
        'mediumturquoise'      : '#48d1cc',
        'mediumvioletred'      : '#c71585',
        'midnightblue'         : '#191970',
        'mintcream'            : '#f5fffa',
        'mistyrose'            : '#ffe4e1',
        'moccasin'             : '#ffe4b5',
        'navajowhite'          : '#ffdead',
        'navy'                 : '#000080',
        'oldlace'              : '#fdf5e6',
        'olive'                : '#808000',
        'olivedrab'            : '#6b8e23',
        'orange'               : '#ffa500',
        'orangered'            : '#ff4500',
        'orchid'               : '#da70d6',
        'palegoldenrod'        : '#eee8aa',
        'palegreen'            : '#98fb98',
        'paleturquoise'        : '#afeeee',
        'palevioletred'        : '#db7093',
        'papayawhip'           : '#ffefd5',
        'peachpuff'            : '#ffdab9',
        'peru'                 : '#cd853f',
        'pink'                 : '#ffc0cb',
        'plum'                 : '#dda0dd',
        'powderblue'           : '#b0e0e6',
        'purple'               : '#800080',
        'red'                  : '#ff0000',
        'rosybrown'            : '#bc8f8f',
        'royalblue'            : '#4169e1',
        'saddlebrown'          : '#8b4513',
        'salmon'               : '#fa8072',
        'sandybrown'           : '#f4a460',
        'seagreen'             : '#2e8b57',
        'seashell'             : '#fff5ee',
        'sienna'               : '#a0522d',
        'silver'               : '#c0c0c0',
        'skyblue'              : '#87ceeb',
        'slateblue'            : '#6a5acd',
        'slategray'            : '#708090',
        'snow'                 : '#fffafa',
        'springgreen'          : '#00ff7f',
        'steelblue'            : '#4682b4',
        'tan'                  : '#d2b48c',
        'teal'                 : '#008080',
        'thistle'              : '#d8bfd8',
        'tomato'               : '#ff6347',
        'turquoise'            : '#40e0d0',
        'violet'               : '#ee82ee',
        'wheat'                : '#f5deb3',
        'white'                : '#ffffff',
        'whitesmoke'           : '#f5f5f5',
        'yellow'               : '#ffff00',
        'yellowgreen'          : '#9acd32'
    }

    def init(self, token):
        color = token[0]
        if color.startswith('#'):
            self.value = color
        else:
            try:
                self.value = self._names[color]
            except KeyError:
                raise TokenError()

    def render(self, context={}):
        return self.value

class Macro(Token):
    macros = {}

    def init(self, token):
        self.name = token[0]
        if isinstance(token[1], Arguments):
            self.args, self.body = token[1].args, token[2:]
        else:
            self.args, self.body = [], token[1:]

        self.__class__.macros[self.name] = self

    def render(self, context={}):
        return '@define %s(%s) {\n  %s\n}' % (self.name, ', '.join(self.args), '\n  '.join(p.render(context) for p in self.body))

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
                for i, val in enumerate(prop.value.values):
                    if isinstance(val, basestring) and val.startswith('$'):
                        prop.value.properties[i] = context.get(val[1:], '')

        return body

class Rule(Token):
    def init(self, token):
        self.selector = token[0]
        self.children = []
        self.properties = []
        for p in token[1:]:
            if isinstance(p, Rule):
                self.children.append(p)
            else:
                self.properties.append(p)

    def render(self, context={}):
        result = ''

        if self.properties:
            result += '%s {\n  %s\n}\n' % (
                self.selector.render(context),
                '\n  '.join(p.render(context) for p in self.properties))

        super_selector = context.get('&', [''])
        children_selector = map(Selector.inherit, product(super_selector, self.selector.values))
        print self.selector.values, super_selector, children_selector
        context['&'] = children_selector
        result += '\n'.join(map(lambda c: c.render(context), self.children))
        context['&'] = super_selector
        return result

class ComplexProperty(Token):
    __slots__ = ('properties',)
    def init(self, token):
        head, tail = token[0], token[1:]
        for t in tail:
            t.name = head + t.name
        self.properties = tail

    def render(self, context={}):
        return '\n  '.join(p.render(context) for p in self.properties)

class Arguments(Token):
    __slots__ = ('args',)
    def init(self, token):
        self.args = list(token)

    def render(self, context={}):
        return ', '.join(self.args)

class Values(Token):
    __slots__ = ('values',)
    def init(self, token):
        self.values = list(token)
    
    def render(self, context={}):
        return ' '.join(p.render(context) for p in self.values)

class Expression(Token):
    __slots__ = ('expression',)
    
    class Op(object):
        ASSO_LEFT = (-1, 0)
        ASSO_RIGHT = (-1,)

        asso = ASSO_LEFT
        prio = 0
        name = ''
        func = None

        def __init__(self, name, prio=0, asso=ASSO_LEFT, func=lambda stack: None):
            self.name = name
            self.prio = prio
            self.asso = asso
            self.func = func

        def __call__(self, stack):
            return stack.append(self.func(stack))

        def __gt__(self, other):
            return cmp(self.prio, other.prio) in self.asso

        def __str__(self):
            return self.name

        __repr__ = __str__

    _operations = {
            '^': Op('^', 3, Op.ASSO_RIGHT, func=lambda s: s.pop() ** s.pop()),
            '*': Op('*', 2, func=lambda s: s.pop() * s.pop()),
            '/': Op('/', 2, func=lambda s: s.pop() / s.pop()),
            '%': Op('%', 2, func=lambda s: s.pop() % s.pop()),
            '+': Op('+', 1, func=lambda s: s.pop() + s.pop()),
            '-': Op('-', 1, func=lambda s: s.pop() - s.pop()),
            }

    def init(self, token):
        self.expression = []
        stack = []
        for item in token:
            if isinstance(item, Value):
                self.expression.append(item)
            elif item in self._operations:
                op = self._operations[item]
                while stack and isinstance(stack[-1], self.Op) and op > stack[-1]:
                    self.expression.append(stack.pop())
                stack.append(op)
            elif item == '(':
                stack.append(item)
            elif item == ')':
                while stack and stack[-1] != '(':
                    self.expression.append(stack.pop())
                if stack:
                    try:
                        stack.pop()
                    except IndexError:
                        raise ArithmeticError('Unbalanched parenthesis in expression')
                else:
                    self.expression.append(item)
            else:
                self.expression.append(item)

        while stack:
            item = stack.pop()
            if item == '(':
                raise ArithmeticError('Unbalanched parenthesis in expression')
            self.expression.append(item)

    def eval(self, context={}):
        stack = []
        for item in self.expression:
            if isinstance(item, self.Op):
                item(stack)
            else:
                stack.append(item)
        return stack.pop()

    def render(self, context={}):
        return self.eval().render(context)

