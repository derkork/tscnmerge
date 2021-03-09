from abc import ABC

from model.Value import Value


class Reference(Value, ABC):
    def __init__(self, id: Value):
        self.id: Value = id

    def is_same(self, other) -> bool:
        if type(self) is not type(other):
            return False

        other_as_reference: Reference = other
        return self.id.is_same(other_as_reference.id)

    def __hash__(self) -> int:
        return self.id.__hash__()
