from abc import ABC
from collections import OrderedDict

from model.CanReferenceExtResource import CanReferenceExtResource
from model.CanReferenceSubResource import CanReferenceSubResource
from model.Comparable import Comparable
from model.ExtResourceReference import ExtResourceReference
from model.SubResourceReference import SubResourceReference
from model.Value import Value


class PropertyBag(CanReferenceExtResource, CanReferenceSubResource, Comparable, ABC):
    def __init__(self):
        self.properties: OrderedDict[str, Value] = OrderedDict()

    def set_property(self, key: str, value: Value):
        self.properties[key] = value

    def get_property(self, key: str) -> Value or None:
        return self.properties.get(key, None)

    def refactor_ext_resource_reference(self, old_id: ExtResourceReference, new_id: ExtResourceReference):
        for prop in self.properties:
            value: Value = self.properties[prop]
            if isinstance(value, CanReferenceExtResource):
                value.refactor_ext_resource_reference(old_id, new_id)
            elif value.is_same(old_id):
                self.properties[prop] = new_id

    def find_sub_resource_references(self, reference: SubResourceReference, prefix: str, paths: set[str]):
        for key, value in self.properties:
            if value.is_same(reference):
                paths.add(f"{prefix}.{key}")
            elif isinstance(value, CanReferenceSubResource):
                value.find_sub_resource_references(reference, f"{prefix}.{key}", paths)

    def find_all_sub_resource_references(self, result: set[SubResourceReference]):
        for key, value in self.properties:
            if isinstance(value, SubResourceReference):
                result.add(value)
            elif isinstance(value, CanReferenceSubResource):
                value.find_all_sub_resource_references(result)

    def refactor_sub_resource_reference(self, old_id: SubResourceReference, new_id: SubResourceReference):
        for key, value in self.properties:
            if isinstance(value, CanReferenceSubResource):
                value.refactor_sub_resource_reference(old_id, new_id)
            elif value.is_same(old_id):
                self.properties[key] = new_id

    def is_same(self, other):
        return self == other

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False

        # noinspection PyTypeChecker
        other_as_property_bag: PropertyBag = other
        if len(self.properties) != len(other_as_property_bag.properties):
            return False

        for key, value in self.properties:
            if key not in other_as_property_bag.properties:
                return False
            if not other_as_property_bag.properties[key].is_same(value):
                return False

    def __hash__(self) -> int:
        # we sort the keys here so same contents yield same hashcode no matter
        # of the actual order of properties in the bag
        sorted_keys: list[str] = sorted(self.properties.keys())
        key_hashes = tuple(map(lambda it: it.__hash__(), sorted_keys))
        value_hashes = tuple(map(lambda it: self.properties[it].__hash__(), sorted_keys))
        return hash(key_hashes + value_hashes)
