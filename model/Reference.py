from abc import ABC

from model.Value import Value


class Reference(Value, ABC):
    def __init__(self, id: Value):
        self.id: Value = id

    def is_same(self, other) -> bool:
        if not type(self) is type(other):
            return False

        other_as_reference: Reference = other
        return self.id.is_same(other_as_reference.id)
