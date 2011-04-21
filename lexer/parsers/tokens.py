
__all__ = ['Token', 'TokenError']

class TokenError(StandardError):
    pass

class Token(object):
    _tokens = ()
    def __init__(self, *token):
        for i, k in enumerate(self._tokens):
            try:
                setattr(self, k, token[i])
            except IndexError:
                setattr(self, k, '')

    def render(self, context={}):
        raise NotImplementedError

    def apply(self, context={}):
        pass

    def __str__(self):
        return self.render()

    def __repr__(self):
        return str(self)

