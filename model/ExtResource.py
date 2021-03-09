from model.Comparable import Comparable
from model.ExtResourceReference import ExtResourceReference
from model.Printable import Printable
from model.Value import Value


class ExtResource(Comparable, Printable):

    def __init__(self, type_: Value, id_: Value, path: Value):
        self.type: Value = type_
        self.id: Value = id_
        self.path: Value = path

    def is_same(self, other):
        if not isinstance(other, ExtResource):
            return False

        return self.id.is_same(other.id) and self.type.is_same(other.type) and self.path.is_same(other.path)

    def to_string(self) -> str:
        return f"[ext_resource path={self.path.to_string()} type={self.type.to_string()} id={self.id.to_string()}]"

    def to_reference(self) -> ExtResourceReference:
        return ExtResourceReference(self.id)
