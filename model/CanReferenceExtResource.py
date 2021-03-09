from abc import ABC, abstractmethod

from model.ExtResourceReference import ExtResourceReference


class CanReferenceExtResource(ABC):

    @abstractmethod
    def refactor_ext_resource_reference(self, old_id: ExtResourceReference, new_id: ExtResourceReference):
        pass
