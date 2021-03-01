from abc import ABC, abstractmethod

from model.Comparable import Comparable
from model.Printable import Printable


class Value(Printable, Comparable, ABC):
    def to_int(self) -> int:
        return int(self.to_string())

    @abstractmethod
    def is_same(self, other) -> bool:
        pass

    def __eq__(self, other) -> bool:
        return self.is_same(other)
