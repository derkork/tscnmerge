from model.Value import Value


class ExtResource:
    _type: Value
    _id: Value
    _path: Value

    def __init__(self, type: Value, id: Value, path: Value):
        self._type = type
        self._id = id
        self._path = path
