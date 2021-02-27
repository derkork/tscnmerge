from model.Value import Value


class Invocation(Value):
    _name: str = ""
    _arguments: list[Value] = []

    def __init__(self, name: str, arguments: list[Value]):
        self._name = name
        self._arguments = arguments
