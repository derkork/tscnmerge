from model.Value import Value


class ScalarValue(Value):
    def __init__(self, value: str):
        self.value: str = value

    def to_string(self) -> str:
        return self.value

    def is_same(self, other: Value) -> bool:
        if type(self) is not type(other):
            return False

        # noinspection PyTypeChecker
        other_as_scalar: ScalarValue = other
        return other_as_scalar.value == self.value

    def __hash__(self) -> int:
        return self.value.__hash__()
