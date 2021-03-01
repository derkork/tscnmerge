import os

from model.Connection import Connection
from model.ContainsExternalReferences import ContainsExternalReferences
from model.ExtResource import ExtResource
from model.ExtResourceReference import ExtResourceReference
from model.GdScene import GdScene
from model.Node import Node
from model.Printable import Printable
from model.SubResource import SubResource
from model.Value import Value


class TscnFile(Printable, ContainsExternalReferences):
    def __init__(self):
        self.gd_scene: GdScene or None = None
        self.ext_resources: list[ExtResource] = []
        self.sub_resources: list[SubResource] = []
        self.nodes: list[Node] = []
        self.connections: list[Connection] = []

    def to_string(self) -> str:
        result = f"{self.gd_scene.to_string()}"

        result += os.linesep
        result += os.linesep
        result += os.linesep.join(map(lambda it: it.to_string(), self.ext_resources))

        result += os.linesep
        result += os.linesep
        result += os.linesep.join(map(lambda it: it.to_string(), self.nodes))

        result += os.linesep

        return result

    def refactor_external_reference(self, old_id: ExtResourceReference, new_id: ExtResourceReference):
        for item in self.sub_resources:
            item.refactor_external_reference(old_id, new_id)
        for item in self.nodes:
            item.refactor_external_reference(old_id, new_id)

    def get_referenced_node(self, reference: Value) -> Node or None:
        return next(filter(lambda it: it.full_path_reference().is_same(reference), self.nodes), None)
