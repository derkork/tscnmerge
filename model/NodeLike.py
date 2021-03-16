from model.PropertyBag import PropertyBag


class NodeLike(PropertyBag):
    def _to_node_like_properties_string(self) -> str:
        result = ""
        # make sure script is always the first property, otherwise godot may not properly load all properties
        if "script" in self.properties:
            result += f"\nscript={self.properties['script'].to_string()}"
        if len(self.properties) > 0:
            result += "\n"
            result += "\n".join(map(lambda t: f"{t[0]} = {t[1].to_string()}",
                                    filter(lambda it: it[0] != "script", self.properties.items())))
            result += "\n"

        return result
