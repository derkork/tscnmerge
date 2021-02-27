from model.PropertyBag import PropertyBag
from model.Value import Value


class Node(PropertyBag):
    _type: Value
    _name: Value
    _parent: Value
    _instance: Value

    def __init__(self, type: Value, name: Value, parent: Value, instance: Value):
        self._type = type
        self._name = name
        self._parent = parent
        self._instance = instance
