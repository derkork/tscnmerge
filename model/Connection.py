from model.Comparable import Comparable
from model.Printable import Printable
from model.Value import Value


class Connection(Printable, Comparable):
    def __init__(self, signal, from_: Value, to: Value, method: Value):
        self.signal: Value = signal
        self.from_: Value = from_
        self.to: Value = to
        self.method: Value = method

    def to_string(self) -> str:
        return f"[connection signal={self.signal.to_string()} " \
               f"from={self.from_.to_string()} to={self.to.to_string()} " \
               f"method={self.method.to_string()}]"

    def is_same(self, other):
        if type(self) != type(other):
            return False

        other_as_connection: Connection = other
        return \
            self.signal.is_same(other_as_connection.signal) and \
            self.from_.is_same(other_as_connection.from_) and \
            self.to.is_same(other_as_connection.to) and \
            self.method.is_same(other_as_connection.method)
