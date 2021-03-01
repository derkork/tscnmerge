from antlr4 import CommonTokenStream, FileStream
from antlr4 import ParseTreeVisitor

from gen.tscn_lexer import tscn_lexer
from gen.tscn_parser import tscn_parser
from model.ArrayValue import ArrayValue
from model.BooleanValue import BooleanValue
from model.Connection import Connection
from model.ExtResource import ExtResource
from model.ExtResourceReference import ExtResourceReference
from model.GdScene import GdScene
from model.Invocation import Invocation
from model.JsonLikeValue import JsonLikeValue
from model.Node import Node
from model.NumericValue import NumericValue
from model.StringValue import StringValue
from model.SubResource import SubResource
from model.SubResourceReference import SubResourceReference
from model.TscnFile import TscnFile
from model.Value import Value


def parse(path: str) -> TscnFile:
    input_stream = FileStream(path)
    lexer = tscn_lexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = tscn_parser(token_stream)
    tree = parser.scene()
    visitor = TscnVisitor()
    return visitor.visitScene(tree)


class TscnVisitor(ParseTreeVisitor):

    def visitScene(self, ctx: tscn_parser.SceneContext) -> TscnFile:
        elements = self.visitChildren(ctx)

        result: TscnFile = TscnFile()

        for element in elements:
            if isinstance(element, GdScene):
                result.gd_scene = element
            if isinstance(element, ExtResource):
                result.ext_resources.append(element)
            if isinstance(element, SubResource):
                result.sub_resources.append(element)
            if isinstance(element, Node):
                result.nodes.append(element)

        return result

    def visitDefinition(self, ctx: tscn_parser.DefinitionContext):
        name: str = ctx.NAME().getText()

        elements = self.visitChildren(ctx)
        header_properties: list[HeaderProperty] = \
            list(filter(lambda x: isinstance(x, HeaderProperty), elements))
        definition_properties: list[DefinitionProperty] = \
            list(filter(lambda x: isinstance(x, DefinitionProperty), elements))

        def property_value(items: list, property_name: str) -> Value:
            value = next(filter(lambda x: x.name == property_name, items), None)
            if value:
                return value.value

        if name == "gd_scene":
            return GdScene(
                property_value(header_properties, "load_steps"),
                property_value(header_properties, "format"),
            )

        if name == "sub_resource":
            result = SubResource(
                property_value(header_properties, "type"),
                property_value(header_properties, "id")
            )
            for item in definition_properties:
                result.set(item.name, item.value)
            return result

        if name == "ext_resource":
            result = ExtResource(
                property_value(header_properties, "type"),
                property_value(header_properties, "id"),
                property_value(header_properties, "path")
            )
            return result

        if name == "node":
            result = Node(
                property_value(header_properties, "type"),
                property_value(header_properties, "name"),
                property_value(header_properties, "parent"),
                property_value(header_properties, "instance")
            )
            for item in definition_properties:
                result.set(item.name, item.value)
            return result

        if name == "connection":
            return Connection(
                property_value(header_properties, "signal"),
                property_value(header_properties, "from"),
                property_value(header_properties, "to"),
                property_value(header_properties, "method")
            )

        assert False, f"Unknown definition type: {name}"

    def visitHeader_property(self, ctx: tscn_parser.Header_propertyContext):
        return HeaderProperty(
            ctx.NAME().getText(), self.visitValue(ctx.value())
        )

    def visitDefinition_property(self, ctx: tscn_parser.Definition_propertyContext):
        return DefinitionProperty(
            ctx.NAME().getText(), self.visitValue(ctx.value())
        )

    def visitValue(self, ctx: tscn_parser.ValueContext):
        return self.visitChildren(ctx)

    def visitString_value(self, ctx: tscn_parser.String_valueContext):
        return StringValue(ctx.STRING_LITERAL().getText())

    def visitNumeric_value(self, ctx: tscn_parser.Numeric_valueContext):
        return NumericValue(ctx.NUMERIC_LITERAL().getText())

    def visitBoolean_value(self, ctx: tscn_parser.Boolean_valueContext):
        return BooleanValue(ctx.BOOLEAN_LITERAL().getText())

    def visitInvocation_value(self, ctx: tscn_parser.Invocation_valueContext):
        name = StringValue(ctx.NAME().getText())
        params = self.visitChildren(ctx)
        if params is None:
            params = []
        if not isinstance(params, list):
            params = [params]

        assert isinstance(params, list)

        if name == "ExtResource":
            return ExtResourceReference(params[0])

        if name == "SubResource":
            return SubResourceReference(params[0])

        return Invocation(name, params)

    def visitArray_value(self, ctx: tscn_parser.Array_valueContext):
        values: list[Value] = self.visitChildren(ctx)
        return ArrayValue(values)

    def visitWhitespace_or_newline(self, _ctx: tscn_parser.Whitespace_or_newlineContext):
        return None

    def visitParameter_list(self, ctx: tscn_parser.Parameter_listContext):
        return self.visitChildren(ctx)

    def visitParameter(self, ctx: tscn_parser.ParameterContext):
        return self.visitChildren(ctx)

    def visitJsonlike_value(self, ctx: tscn_parser.Jsonlike_valueContext):
        properties = self.visitChildren(ctx)

        if properties is None:
            properties = []

        if not isinstance(properties, list):
            properties = [properties]

        result = JsonLikeValue()
        for item in properties:
            result.set(item.name, item.value)

        return result

    def visitJsonlike_property_list(self, ctx: tscn_parser.Jsonlike_property_listContext):
        return self.visitChildren(ctx)

    def visitJsonlike_property(self, ctx: tscn_parser.Jsonlike_propertyContext):
        return JsonLikeProperty(ctx.STRING_LITERAL().getText(), self.visitValue(ctx.value()))

    def aggregateResult(self, aggregate, next_result):
        if next_result is None:
            return aggregate

        if isinstance(aggregate, list):
            aggregate.append(next_result)
            return aggregate

        if aggregate is None:
            return next_result

        return [aggregate, next_result]


class GenericProperty:
    name: str = ""
    value: Value = None

    def __init__(self, name: str, value: Value):
        self.name = name
        self.value = value


class HeaderProperty(GenericProperty):
    pass


class DefinitionProperty(GenericProperty):
    pass


class JsonLikeProperty(GenericProperty):
    pass
