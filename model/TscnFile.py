from model.Connection import Connection
from model.ExtResource import ExtResource
from model.GdScene import GdScene
from model.Node import Node
from model.SubResource import SubResource


class TscnFile:
    gd_scene: GdScene = None
    ext_resources: list[ExtResource] = []
    sub_resources: list[SubResource] = []
    nodes: list[Node] = []
    connections: list[Connection] = []

