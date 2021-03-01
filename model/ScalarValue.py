from model.Value import Value


class ScalarValue(Value):
    def __init__(self, value: str):
        self.value: str = value

    def to_string(self) -> str:
        return self.value

    def is_same(self, other: Value) -> bool:
        if not type(self) is type(other):
            return False

        # noinspection PyTypeChecker
        other_as_scalar: ScalarValue = other
        return other_as_scalar.value == self.value
