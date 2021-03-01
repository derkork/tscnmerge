from abc import ABC, abstractmethod


class Comparable(ABC):
    @abstractmethod
    def is_same(self, other):
        pass
