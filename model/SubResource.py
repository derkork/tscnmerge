from model.PropertyBag import PropertyBag
from model.Value import Value


class SubResource(PropertyBag):
    def __init__(self, type: Value, id: Value):
        super().__init__()
        self.type: Value = type
        self.id: Value = id
