from abc import ABC, abstractmethod

from model.SubResourceReference import SubResourceReference
from model.Value import Value


class CanReferenceSubResource(ABC):

    @abstractmethod
    def find_sub_resource_references(self, reference: SubResourceReference, prefix: str, paths: set[str]):
        pass

    @abstractmethod
    def find_all_sub_resource_references(self, result: set[SubResourceReference]):
        pass

    @abstractmethod
    def refactor_sub_resource_reference(self, old_id: SubResourceReference, new_id: SubResourceReference):
        pass
