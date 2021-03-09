from model.CanReferenceExtResource import CanReferenceExtResource
from model.CanReferenceSubResource import CanReferenceSubResource
from model.ExtResourceReference import ExtResourceReference
from model.SubResourceReference import SubResourceReference
from model.Value import Value


class ArrayValue(Value, CanReferenceExtResource, CanReferenceSubResource):
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

    def refactor_ext_resource_reference(self, old_id: ExtResourceReference, new_id: ExtResourceReference):
        for idx, value in enumerate(self.values):
            if isinstance(value, CanReferenceExtResource):
                value.refactor_ext_resource_reference(old_id, new_id)
            elif value.is_same(old_id):
                self.values[idx] = new_id

    def find_sub_resource_references(self, reference: SubResourceReference, prefix: str, paths: set[str]):
        for value in self.values:
            if reference.is_same(value):
                paths.add(prefix)
            if isinstance(value, CanReferenceSubResource):
                value.find_sub_resource_references(reference, prefix, paths)

    def find_all_sub_resource_references(self, result: set[SubResourceReference]):
        for value in self.values:
            if isinstance(value, SubResourceReference):
                result.add(value)
            elif isinstance(value, CanReferenceSubResource):
                value.find_all_sub_resource_references(result)

    def refactor_sub_resource_reference(self, old_id: SubResourceReference, new_id: SubResourceReference):
        for idx, value in self.values:
            if value.is_same(old_id):
                self.values[idx] = new_id
            elif isinstance(value, CanReferenceSubResource):
                value.refactor_sub_resource_reference(old_id, new_id)

    def to_string(self) -> str:
        result = "[ "
        result += ",".join(map(lambda it: it.to_string(), self.values))
        result += "]"
        return result

    def __hash__(self) -> int:
        return hash(tuple(map(lambda it: it.__hash__(), self.values)))
