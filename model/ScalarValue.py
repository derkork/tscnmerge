from model.Value import Value


class ScalarValue(Value):
    _value: str = ""

    def __init__(self, value: str):
        self._value = value

    def to_string(self) -> str:
        return self._value

    def is_same(self, other: Value) -> bool:
        if not type(self) is type(other):
            return False

        # noinspection PyProtectedMember
        return other._value == self._value
