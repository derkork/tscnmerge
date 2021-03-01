from model.ContainsExternalReferences import ContainsExternalReferences
from model.ExtResourceReference import ExtResourceReference
from model.Value import Value


class ArrayValue(Value, ContainsExternalReferences):
    def __init__(self, values: list[Value]):
        self.values: list[Value] = values

    def is_same(self, other) -> bool:
        if not isinstance(other, ArrayValue):
            return False

        if len(self.values) != len(other.values):
            return False

        for idx, value in enumerate(self.values):
            if not value.is_same(other.values[idx]):
                return False

        return True

    def refactor_external_reference(self, old_id: ExtResourceReference, new_id: ExtResourceReference):
        for idx, value in enumerate(self.values):
            if isinstance(value, ContainsExternalReferences):
                value.refactor_external_reference(old_id, new_id)
            elif value.is_same(old_id):
                self.values[idx] = new_id
