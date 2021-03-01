import os

from model.PropertyBag import PropertyBag
from model.Value import Value


class JsonLikeValue(Value, PropertyBag):
    def is_same(self, other) -> bool:
        if not isinstance(other, JsonLikeValue):
            return False

        for key, value in self.properties.items():
            if not other.get(key) == value:
                return False

        return True

    def to_string(self) -> str:
        result = "{"
        result += os.linesep
        result += os.linesep.join(map(lambda t: f"{t[0]}: {t[1].to_string()}", self.properties.items()))
        result += os.linesep
        result += "}"
        return result
