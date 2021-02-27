from model.PropertyBag import PropertyBag
from model.Value import Value


class SubResource(PropertyBag):
    _type: Value
    _id:  Value

    def __init__(self, type: Value, id: Value):
        self._type = type
        self._id = id
