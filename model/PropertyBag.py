from model.ContainsExternalReferences import ContainsExternalReferences
from model.ExtResourceReference import ExtResourceReference
from model.Value import Value


class PropertyBag(ContainsExternalReferences):
    def __init__(self):
        self.properties: dict[str, Value] = {}

    def set(self, key: str, value: Value):
        self.properties[key] = value

    def get(self, key: str) -> Value or None:
        return self.properties.get(key, None)

    def refactor_external_reference(self, old_id: ExtResourceReference, new_id: ExtResourceReference):
        for prop in self.properties:
            value: Value = self.properties[prop]
            if isinstance(value, ContainsExternalReferences):
                value.refactor_external_reference(old_id, new_id)
            elif value.is_same(old_id):
                self.properties[prop] = new_id
