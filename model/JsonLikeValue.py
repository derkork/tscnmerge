from model.PropertyBag import PropertyBag
from model.Value import Value


class JsonLikeValue(PropertyBag, Value):
    def is_same(self, other) -> bool:
        if not isinstance(other, JsonLikeValue):
            return False

        for key, value in self.properties.items():
            if not other.get_property(key) == value:
                return False

        return True

    def to_string(self) -> str:
        result = "{"
        result += "\n"
        result += "\n".join(map(lambda t: f"{t[0]}: {t[1].to_string()}", self.properties.items()))
        result += "\n"
        result += "}"
        return result

    def __hash__(self) -> int:
        return super().__hash__()

