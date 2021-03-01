from model.Reference import Reference


class ExtResourceReference(Reference):
    def to_string(self) -> str:
        return f"ExtResource( {self.id.to_string()} )"
