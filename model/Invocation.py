from model.Value import Value


class Invocation(Value):
    def __init__(self, name: Value, arguments: list[Value]):
        self.name: Value = name
        self.arguments: list[Value] = arguments

    def to_string(self) -> str:
        return f"{self.name.to_string()}( {','.join(map(lambda it: it.to_string(), self.arguments))} )"

    def is_same(self, other) -> bool:
        if type(self) != type(other):
            return False

        other_as_invocation: Invocation = other
        if not self.name.is_same(other_as_invocation.name):
            return False

        if len(self.arguments) != len(other_as_invocation.arguments):
            return False

        for index, value in enumerate(self.arguments):
            if not value.is_same(other_as_invocation.arguments[index]):
                return False

        return True
