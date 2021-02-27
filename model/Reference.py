from model.Value import Value


class Reference(Value):
    _id: Value

    def __init__(self, id: Value):
        _id = id

    def is_same(self, other) -> bool:
        # noinspection PyProtectedMember
        return type(self) is type(other) and self._id.is_same(other._id)
