from model.Value import Value


class GdScene:
    _load_steps: Value
    _format: Value

    def __init__(self, load_steps: Value, format_: Value):
        self._load_steps = load_steps
        self._format = format_
