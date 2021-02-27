class Value:

    def to_string(self) -> str:
        pass

    def to_int(self) -> int:
        return int(self.to_string())

    # noinspection PyMethodMayBeStatic
    def is_same(self, other) -> bool:
        return False
