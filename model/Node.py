from model.ExtResourceReference import ExtResourceReference
from model.NodeLike import NodeLike
from model.Printable import Printable
from model.StringValue import StringValue
from model.Value import Value


class Node(NodeLike, Printable):
    def __init__(self, type: Value, name: Value, parent: Value, instance: Value, instance_placeholder: Value):
        super().__init__()
        self.type: Value or None = type
        self.name: Value = name
        self.parent: Value or None = parent
        self.instance: Value or None = instance
        self.instance_placeholder: Value or None = instance_placeholder

    def is_root(self) -> bool:
        return self.parent is None

    def represents_same_thing(self, other: 'Node') -> bool:
        # Two nodes represent the same thing if they have the same type
        # the same script and the same instance they refer to.
        # Note that this function only works correctly _AFTER_ the
        # external resources have been consolidated.

        def are_same(first: Value, second: Value) -> bool:
            if bool(first is None) ^ bool(second is None):
                return False

            if first is not None:
                assert second is not None
                if not first.is_same(second):
                    return False

            return True

        return \
            are_same(self.type, other.type) and \
            are_same(self.get_property("script"), other.get_property("script")) and \
            are_same(self.instance, other.instance) and \
            are_same(self.instance_placeholder, other.instance_placeholder)

    def refactor_ext_resource_reference(self, old_id: ExtResourceReference, new_id: ExtResourceReference):
        if self.instance is not None and self.instance.is_same(old_id):
            self.instance = new_id

        super().refactor_ext_resource_reference(old_id, new_id)

    def full_path_reference(self) -> Value:
        # Godot has some idiosyncracies when it comes to referencing parent nodes, so we will need to
        # work around them.

        # The root node is referred to as "."
        if self.parent is None:
            return StringValue('"."')

        # Nodes directly below the root node are referred to by their name only
        if self.parent.to_string() == '"."':
            return self.name

        # Nodes below the first layer use a ParentName/OwnName notation to be referred to
        return StringValue('"' + self.parent.to_string().replace('"', '') +
                           "/" + self.name.to_string().replace('"', '') + '"')

    def to_string(self) -> str:
        result = f"[node name={self.name.to_string()}"
        if self.type is not None:
            result += f" type={self.type.to_string()}"
        if self.parent is not None:
            result += f" parent={self.parent.to_string()}"
        if self.instance is not None:
            result += f" instance={self.instance.to_string()}"
        result += "]"
        result += "\n"
        result += super()._to_node_like_properties_string()
        result += "\n"
        return result
