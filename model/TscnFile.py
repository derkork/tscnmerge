from model.Connection import Connection
from model.ExtResource import ExtResource
from model.ExtResourceReference import ExtResourceReference
from model.GdScene import GdScene
from model.Node import Node
from model.Printable import Printable
from model.SubResource import SubResource
from model.SubResourceReference import SubResourceReference


class TscnFile(Printable):
    def __init__(self):
        self.gd_scene: GdScene or None = None
        self.ext_resources: list[ExtResource] = []
        self.sub_resources: list[SubResource] = []
        self.nodes: list[Node] = []
        self.connections: list[Connection] = []

    def to_string(self) -> str:
        result = f"{self.gd_scene.to_string()}"
        result += "\n"
        result += "\n"
        if len(self.sub_resources) > 0:
            result += "\n".join(map(lambda it: it.to_string(), self.sub_resources))
            result += "\n"
            result += "\n"

        if len(self.ext_resources) > 0:
            result += "\n".join(map(lambda it: it.to_string(), self.ext_resources))
            result += "\n"
            result += "\n"

        result += "\n".join(map(lambda it: it.to_string(), self.nodes))
        result += "\n"
        result += "\n"

        if len(self.connections) > 0:
            result += "\n".join(map(lambda it: it.to_string(), self.connections))
            result += "\n"

        return result

    def refactor_ext_resource_reference(self, old_id: ExtResourceReference, new_id: ExtResourceReference):
        for item in self.sub_resources:
            item.refactor_ext_resource_reference(old_id, new_id)
        for item in self.nodes:
            item.refactor_ext_resource_reference(old_id, new_id)

    def refactor_sub_resource_reference(self, old_id: SubResourceReference, new_id: SubResourceReference):
        for resource in self.sub_resources:
            if resource.id.is_same(old_id.id):
                resource.id = new_id.id
            resource.refactor_sub_resource_reference(old_id, new_id)

        for node in self.nodes:
            node.refactor_sub_resource_reference(old_id, new_id)
