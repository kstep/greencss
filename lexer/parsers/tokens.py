
__all__ = ['Token', 'TokenError']

class TokenError(StandardError):
    pass

class Token(object):

    def __new__(cls, parser=None):
        if parser:
            def wrapper(inp):
                token, rest = parser(inp)
                if not token:
                    return token, rest

                self = cls()
                try:
                    self.init(token)
                except TokenError:
                    return None, inp

                return [self], rest
            return wrapper

        return object.__new__(cls)

    def init(self, token):
        for i, k in enumerate(self.__slots__):
            try:
                setattr(self, k, token[i])
            except IndexError:
                setattr(self, k, '')

    def render(self, parent=None):
        raise NotImplementedError

    def __str__(self):
        return self.render()

    def __repr__(self):
        return str(self)

