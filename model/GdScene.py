from model.Printable import Printable
from model.Value import Value


class GdScene(Printable):
    def __init__(self, load_steps: Value, format_: Value):
        self.load_steps: Value = load_steps
        self.format: Value = format_

    def to_string(self) -> str:
        return f"[gd_scene load_steps={self.load_steps.to_string()} format={self.format.to_string()}]"
