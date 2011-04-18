
class state(object):

    stack = []
    token = []
    parser = None

    @classmethod
    def push(cls, parser):

        def save_state(inp):
            token, rest = parser(inp)
            if token is not None:
                st = cls()
                st.parser = parser
                st.token = token
                cls.stack.append(st)
            return token, rest

        return save_state

    @classmethod
    def pop(cls, inp):
        return cls._check(inp, cls.stack.pop())

    @classmethod
    def check(cls, inp):
        return cls._check(inp, cls.stack[-1])

    @classmethod
    def _check(cls, inp, st):
        token, rest = st.parser(inp)
        if token != st.token:
            return None, inp
        return token, rest

    @classmethod
    def drop(cls, inp):
        cls.stack.pop()
        return [], inp

