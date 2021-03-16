from model.NodeLike import NodeLike
from model.Printable import Printable
from model.PropertyBag import PropertyBag
from model.SubResourceReference import SubResourceReference
from model.Value import Value


class SubResource(NodeLike, Printable):
    def __init__(self, type: Value, id: Value):
        super().__init__()
        self.type: Value = type
        self.id: Value = id
        # The path_ids are used for diffing and merging to mark sub resources
        # which belong together
        self.path_ids: set[str] = set()

    def is_same(self, other) -> bool:
        if type(self) is not type(other):
            return False

        other_as_sub_resource: SubResource = other
        if not self.id.is_same(other.id):
            return False

        return self.has_same_type_and_properties(other_as_sub_resource)

    def represents_same_thing(self, other: 'SubResource') -> bool:
        # We assume them to be the same thing if they have the same type
        return other.type.is_same(self.type)

    def has_same_type_and_properties(self, other: 'SubResource') -> bool:
        if not self.type.is_same(other.type):
            return False

        return super().is_same(other)

    def shares_paths_with(self, other: 'SubResource') -> bool:
        return len(self.path_ids.intersection(other.path_ids)) > 0

    def to_reference(self) -> SubResourceReference:
        return SubResourceReference(self.id)

    def to_string(self) -> str:
        result = f"[sub_resource type={self.type.to_string()} id={self.id.to_string()}]"
        result += super()._to_node_like_properties_string()
        result += "\n"
        return result
