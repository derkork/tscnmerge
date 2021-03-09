from model.Reference import Reference


class SubResourceReference(Reference):
    def to_string(self) -> str:
        return f"SubResource( {self.id.to_string()} )"

