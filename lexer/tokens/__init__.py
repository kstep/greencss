from __future__ import with_statement
from greencss.lexer.parsers.tokens import Token, TokenError
from greencss.lexer.parsers.state import state
from itertools import product
import colorsys

def apply_context(alist, context={}):
    return map(lambda i: i.apply(context) or i, alist)

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
        val = Value(float(val1) / koeff2 * koeff1, val2.unit)
        return val, val2

    @classmethod
    def coerce(cls, meth):
        def wrapper(self, other):
            if not isinstance(other, Value):
                if hasattr(other, meth.__name__):
                    return getattr(other, meth.__name__)(self)
                raise NotImplementedError()

            a, b = cls.convert(self, other)
            return Value(meth(a, b), a.unit)
        return wrapper

class PseudoCall(Token):
    _tokens = ('name', 'args')
    def __init__(self, *token):
        self.name, self.args = token[0], token[1]

    def render(self, context={}):
        return '%s(%s)' % (self.name, self.args)

class String(Token):
    _tokens = ('value',)

    def render(self, context={}):
        if " " in self.value:
            return '"' + self.value + '"'
        else:
            return self.value

    def length(self):
        return Value(len(self.value), '')

class Value(Token):
    _tokens = ('value', 'unit')

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
    def __init__(self, *token):
        self.values = token

    @staticmethod
    def inherit(pair):
        base, s = pair
        return (s.replace('&', base) if '&' in s else base + ' ' + s).strip()

    def render(self, context={}):
        base = context.get('&', [''])
        return ', '.join(map(self.inherit, product(base, self.values)))

class Property(Token):
    _tokens = ('name', 'value')
    def render(self, context={}):
        return '%s: %s;' % (self.name, self.value.render(context))

    def apply(self, context={}):
        self.value = self.value.apply(context) or self.value

class Variable(Token):
    variables = {}
    instance = None

    def __init__(self, *token):
        self.__class__.variables[token[0]] = token[1]

    def render(self, context={}):
        return str(self.variables)

    @classmethod
    def is_in_macro(cls):
        return state.stack and state.stack[-1].token and '@define' in state.stack[-1].token

    @classmethod
    def get(cls, token):
        name = token[0]
        try:
            return cls.variables[name]
        except KeyError:
            if cls.is_in_macro():
                value = cls.var(name)
                cls.variables[name] = value
                return value

            raise NameError('Variable \'%s\' is not defined' % (name))

    class var(object):
        def __init__(self, name=''):
            self.name = name

        def apply(self, context={}):
            value = context.get(self.name, None) or Variable.variables.get(self.name, None)
            if value is None or value is self:
                raise NameError('Variable \'%s\' is not defined' % (self.name))
            return value

class Color(Token):
    _tokens = ('red', 'green', 'blue')
    _names = {
        'aliceblue'            : (240, 248, 255), 
        'antiquewhite'         : (250, 235, 215), 
        'aqua'                 : (0  , 255, 255), 
        'aquamarine'           : (127, 255, 212), 
        'azure'                : (240, 255, 255), 
        'beige'                : (245, 245, 220), 
        'bisque'               : (255, 228, 196), 
        'black'                : (0  , 0  , 0)  , 
        'blanchedalmond'       : (255, 235, 205), 
        'blue'                 : (0  , 0  , 255), 
        'blueviolet'           : (138, 43 , 226), 
        'brown'                : (165, 42 , 42) , 
        'burlywood'            : (222, 184, 135), 
        'cadetblue'            : (95 , 158, 160), 
        'chartreuse'           : (127, 255, 0)  , 
        'chocolate'            : (210, 105, 30) , 
        'coral'                : (255, 127, 80) , 
        'cornflowerblue'       : (100, 149, 237), 
        'cornsilk'             : (255, 248, 220), 
        'crimson'              : (220, 20 , 60) , 
        'cyan'                 : (0  , 255, 255), 
        'darkblue'             : (0  , 0  , 139), 
        'darkcyan'             : (0  , 139, 139), 
        'darkgoldenrod'        : (184, 134, 11) , 
        'darkgray'             : (169, 169, 169), 
        'darkgreen'            : (0  , 100, 0)  , 
        'darkkhaki'            : (189, 183, 107), 
        'darkmagenta'          : (139, 0  , 139), 
        'darkolivegreen'       : (85 , 107, 47) , 
        'darkorange'           : (255, 140, 0)  , 
        'darkorchid'           : (153, 50 , 204), 
        'darkred'              : (139, 0  , 0)  , 
        'darksalmon'           : (233, 150, 122), 
        'darkseagreen'         : (143, 188, 143), 
        'darkslateblue'        : (72 , 61 , 139), 
        'darkslategray'        : (47 , 79 , 79) , 
        'darkturquoise'        : (0  , 206, 209), 
        'darkviolet'           : (148, 0  , 211), 
        'deeppink'             : (255, 20 , 147), 
        'deepskyblue'          : (0  , 191, 255), 
        'dimgray'              : (105, 105, 105), 
        'dodgerblue'           : (30 , 144, 255), 
        'firebrick'            : (178, 34 , 34) , 
        'floralwhite'          : (255, 250, 240), 
        'forestgreen'          : (34 , 139, 34) , 
        'fuchsia'              : (255, 0  , 255), 
        'gainsboro'            : (220, 220, 220), 
        'ghostwhite'           : (248, 248, 255), 
        'gold'                 : (255, 215, 0)  , 
        'goldenrod'            : (218, 165, 32) , 
        'gray'                 : (128, 128, 128), 
        'green'                : (0  , 128, 0)  , 
        'greenyellow'          : (173, 255, 47) , 
        'honeydew'             : (240, 255, 240), 
        'hotpink'              : (255, 105, 180), 
        'indianred'            : (205, 92 , 92) , 
        'indigo'               : (75 , 0  , 130), 
        'ivory'                : (255, 255, 240), 
        'khaki'                : (240, 230, 140), 
        'lavender'             : (230, 230, 250), 
        'lavenderblush'        : (255, 240, 245), 
        'lawngreen'            : (124, 252, 0)  , 
        'lemonchiffon'         : (255, 250, 205), 
        'lightblue'            : (173, 216, 230), 
        'lightcoral'           : (240, 128, 128), 
        'lightcyan'            : (224, 255, 255), 
        'lightgoldenrodyellow' : (250, 250, 210), 
        'lightgreen'           : (144, 238, 144), 
        'lightgrey'            : (211, 211, 211), 
        'lightpink'            : (255, 182, 193), 
        'lightsalmon'          : (255, 160, 122), 
        'lightseagreen'        : (32 , 178, 170), 
        'lightskyblue'         : (135, 206, 250), 
        'lightslategray'       : (119, 136, 153), 
        'lightsteelblue'       : (176, 196, 222), 
        'lightyellow'          : (255, 255, 224), 
        'lime'                 : (0  , 255, 0)  , 
        'limegreen'            : (50 , 205, 50) , 
        'linen'                : (250, 240, 230), 
        'magenta'              : (255, 0  , 255), 
        'maroon'               : (128, 0  , 0)  , 
        'mediumaquamarine'     : (102, 205, 170), 
        'mediumblue'           : (0  , 0  , 205), 
        'mediumorchid'         : (186, 85 , 211), 
        'mediumpurple'         : (147, 112, 219), 
        'mediumseagreen'       : (60 , 179, 113), 
        'mediumslateblue'      : (123, 104, 238), 
        'mediumspringgreen'    : (0  , 250, 154), 
        'mediumturquoise'      : (72 , 209, 204), 
        'mediumvioletred'      : (199, 21 , 133), 
        'midnightblue'         : (25 , 25 , 112), 
        'mintcream'            : (245, 255, 250), 
        'mistyrose'            : (255, 228, 225), 
        'moccasin'             : (255, 228, 181), 
        'navajowhite'          : (255, 222, 173), 
        'navy'                 : (0  , 0  , 128), 
        'oldlace'              : (253, 245, 230), 
        'olive'                : (128, 128, 0)  , 
        'olivedrab'            : (107, 142, 35) , 
        'orange'               : (255, 165, 0)  , 
        'orangered'            : (255, 69 , 0)  , 
        'orchid'               : (218, 112, 214), 
        'palegoldenrod'        : (238, 232, 170), 
        'palegreen'            : (152, 251, 152), 
        'paleturquoise'        : (175, 238, 238), 
        'palevioletred'        : (219, 112, 147), 
        'papayawhip'           : (255, 239, 213), 
        'peachpuff'            : (255, 218, 185), 
        'peru'                 : (205, 133, 63) , 
        'pink'                 : (255, 192, 203), 
        'plum'                 : (221, 160, 221), 
        'powderblue'           : (176, 224, 230), 
        'purple'               : (128, 0  , 128), 
        'red'                  : (255, 0  , 0)  , 
        'rosybrown'            : (188, 143, 143), 
        'royalblue'            : (65 , 105, 225), 
        'saddlebrown'          : (139, 69 , 19) , 
        'salmon'               : (250, 128, 114), 
        'sandybrown'           : (244, 164, 96) , 
        'seagreen'             : (46 , 139, 87) , 
        'seashell'             : (255, 245, 238), 
        'sienna'               : (160, 82 , 45) , 
        'silver'               : (192, 192, 192), 
        'skyblue'              : (135, 206, 235), 
        'slateblue'            : (106, 90 , 205), 
        'slategray'            : (112, 128, 144), 
        'snow'                 : (255, 250, 250), 
        'springgreen'          : (0  , 255, 127), 
        'steelblue'            : (70 , 130, 180), 
        'tan'                  : (210, 180, 140), 
        'teal'                 : (0  , 128, 128), 
        'thistle'              : (216, 191, 216), 
        'tomato'               : (255, 99 , 71) , 
        'turquoise'            : (64 , 224, 208), 
        'violet'               : (238, 130, 238), 
        'wheat'                : (245, 222, 179), 
        'white'                : (255, 255, 255), 
        'whitesmoke'           : (245, 245, 245), 
        'yellow'               : (255, 255, 0)  , 
        'yellowgreen'          : (154, 205, 50)
    }

    def __init__(self, *token):
        if len(token) == 1:
            try:
                color = self._names[token[0]]
            except KeyError:
                raise TokenError()
            r, g, b = color

        else:
            try:
                mode = {
                        'rgb': lambda r, g, b: (r, g, b),
                        'hls': colorsys.hls_to_rgb,
                        'hsv': colorsys.hsv_to_rgb,
                        'yiq': colorsys.yiq_to_rgb
                        }[token[0]]
            except KeyError:
                raise TokenError()

            r, g, b = mode(*token[1:])

        self.red, self.green, self.blue = r, g, b

    def hex(self):
        return '#%02x%02x%02x' % (self.red, self.green, self.blue)

    def rgb(self):
        return 'rgb(%d, %d, %d)' % (self.red, self.green, self.blue)

    def darken(self, args=None):
        if args:
            amount = args.values[0].value
            amount, unit = int(amount.value), amount.unit
        else:
            amount, unit = 10, '%'

        h, l, s = colorsys.rgb_to_hls(self.red, self.green, self.blue)

        if unit == '%':
            l *= amount / 100.0
        else:
            l -= amount / 100.0

        if l < 0:
            l = 0.0

        return Color('hls', h, l, s)

    def brighten(self, args=None):
        if args:
            amount = args.values[0].value
            amount, unit = int(amount.value), amount.unit
        else:
            amount, unit = 10.0, '%'

        h, l, s = colorsys.rgb_to_hls(self.red, self.green, self.blue)

        if unit == '%':
            l *= 1.0 + amount / 100.0
        else:
            l += amount / 100.0

        if l < 0:
            l = 0.0

        return Color('hls', h, l, s)

    def render(self, context={}):
        return self.hex()

    def boundcheck(self, value):
        if value < 0:
            return 0
        elif value > 255:
            return 255
        else:
            return value

    def __add__(self, other):
        r = self.boundcheck(self.red + other.red)
        g = self.boundcheck(self.green + other.green)
        b = self.boundcheck(self.blue + other.blue)

        return Color('rgb', r, g, b)

    def __sub__(self, other):
        r = self.boundcheck(self.red - other.red)
        g = self.boundcheck(self.green - other.green)
        b = self.boundcheck(self.blue - other.blue)

        return Color('rgb', r, g, b)

    def __mul__(self, other):
        if isinstance(other, Color):
            r, g, b = other.red, other.green, other.blue
        else:
            v = int(other.value)
            r, g, b = v, v, v

        r = self.boundcheck(self.red * r)
        g = self.boundcheck(self.green * g)
        b = self.boundcheck(self.blue * b)

        return Color('rgb', r, g, b)

    def __div__(self, other):
        if isinstance(other, Color):
            r, g, b = other.red, other.green, other.blue
        else:
            v = int(other.value)
            r, g, b = v, v, v

        r = self.boundcheck(self.red / r)
        g = self.boundcheck(self.green / g)
        b = self.boundcheck(self.blue / b)

        return Color('rgb', r, g, b)

class Macro(Token):
    macros = {}

    def __init__(self, *token):
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
        name, args = token[0], token[1:]

        try:
            macro = cls.macros[name]
        except KeyError:
            raise NameError('Macro \'%s\' is not defined' % (name))

        if len(macro.args) != len(args):
            raise TypeError('Macro %s requires exactly %d arguments (%d given)' % (macro.name,
                len(macro.args), len(args)))

        context = dict(zip(macro.args, args))
        from copy import deepcopy as copy
        body = copy(macro.body)
        body = apply_context(body, context)
        return body

class Rule(Token):
    def __init__(self, *token):
        self.selector = token[0]
        self.children = []
        self.properties = []
        for p in token[1:]:
            if isinstance(p, Rule):
                self.children.append(p)
            else:
                self.properties.append(p)

    def apply(self, context={}):
        self.properties = apply_context(self.properties, context)
        self.children = apply_context(self.children, context)

    def render(self, context={}):
        result = ''

        if self.properties:
            result += '%s {\n  %s\n}\n' % (
                self.selector.render(context),
                '\n  '.join(p.render(context) for p in self.properties))

        super_selector = context.get('&', [''])
        children_selector = map(Selector.inherit, product(super_selector, self.selector.values))
        context['&'] = children_selector

        if self.children:
            result += '\n'.join(map(lambda c: c.render(context), self.children))

        context['&'] = super_selector

        return result

def ComplexProperty(token):
    head, tail = token[0], token[1:]
    for t in tail:
        t.name = head + t.name
    return tail

class Arguments(Token):
    _tokens = ('args',)
    def __init__(self, *token):
        self.args = list(token)

    def render(self, context={}):
        return ', '.join(self.args)

class Values(Token):
    _tokens = ('values',)
    def __init__(self, *token):
        self.values = list(token)
    
    def render(self, context={}):
        return ' '.join(p.render(context) for p in self.values)

    def apply(self, context={}):
        self.values = apply_context(self.values, context)

class Expression(Token):
    _tokens = ('expression',)
    
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

        def apply(self, context={}):
            pass

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

    def __init__(self, *token):
        self._value = None
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

    def eval(self):
        if self._value is None:
            stack = []
            for item in self.expression:
                if isinstance(item, self.Op):
                    item(stack)
                else:
                    stack.append(item)
            self._value = stack.pop()
        return self._value
    value = property(eval)

    def render(self, context={}):
        return self.value.render(context)

    def apply(self, context={}):
        self.expression = apply_context(self.expression, context)

def MethodCall(token):
    if len(token) == 1:
        return token
    
    value, method, args = token[0], token[1], token[2:]
    if Variable.is_in_macro():
        class var(object):
            def apply(self, context={}):
                self.value = self.value.apply(context) or self.value
                return getattr(self.value, self.method)(*self.args)

        result = var()
        result.value = value
        result.method = method
        result.args = args
    else:
        result = getattr(value, method)(*args)
    
    return result

def IncludeFile(token):
    from greencss.lexer.parsers.helpers import clear_lines
    from greencss import _parser

    filename = token[0]
    with open(filename, 'rb') as f:
        data = clear_lines(f.read())
    token, rest = _parser(data)
    return token or []

class Metablock(Token):
    def __init__(self, *token):
        self.name = token[0]
        if isinstance(token[1], Values):
            self.args, self.body = token[1].values, token[2:]
        else:
            self.args, self.body = [], token[1:]

    def apply(self, context={}):
        self.args = apply_context(self.args, context)
        self.body = apply_context(self.body, context)

    def render(self, context={}):
        return '%s %s {\n%s}\n' % (self.name, ', '.join(a.render(context) for a in self.args),
                ''.join(b.render(context) for b in self.body))

