from abc import ABC, abstractmethod

from model.ExtResourceReference import ExtResourceReference


class ContainsExternalReferences(ABC):

    @abstractmethod
    def refactor_external_reference(self, old_id: ExtResourceReference, new_id: ExtResourceReference):
        pass
