from abc import ABC, abstractmethod


class Printable(ABC):
    @abstractmethod
    def to_string(self) -> str:
        pass
