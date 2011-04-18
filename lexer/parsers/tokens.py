class Token(object):
    parser = None

    def __init__(self, parser=None, token=[]):
        self.__name__ = self.__class__.__name__
        self.parser = parser
        if token:
            self.init(token)

    def init(self, token):
        for i, k in enumerate(self.__slots__):
            try:
                setattr(self, k, token[i])
            except IndexError:
                setattr(self, k, '')

    def __call__(self, inp):
        token, rest = self.parser(inp)
        if token is not None:
            token = [self.__class__(token=token)]
        return token, rest

    def __str__(self):
        return ''.join(str(getattr(self, k, '')) for k in self.__slots__)

    def __repr__(self):
        return str(self)

