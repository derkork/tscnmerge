from model.Value import Value


class Connection:
    _signal: Value
    _from: Value
    _to: Value
    _method: Value

    def __init__(self, signal, from_: Value, to: Value, method: Value):
        self._signal = signal
        self._from = from_
        self._to = to
        self._method = method
