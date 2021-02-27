from model.Value import Value


class ArrayValue(Value):
    _values: list[Value] = []

    def __init__(self, values: list[Value]):
        self._values = values

    def is_same(self, other) -> bool:
        if not isinstance(other, ArrayValue):
            return False

        if len(self._values) != len(other._values):
            return False

        for idx, value in enumerate(self._values):
            if not value.is_same(other._values[idx]):
                return False

        return True


