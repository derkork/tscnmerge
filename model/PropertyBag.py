from model.Value import Value


class PropertyBag:
    _properties: dict[str, Value] = {}

    def set(self, key: str, value: Value):
        self._properties[key] = value
