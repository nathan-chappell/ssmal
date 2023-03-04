from dataclasses import dataclass
from typing import TypeVar

Self = TypeVar("Self", bound="LineWriter")


@dataclass
class Line:
    indent: int
    text: str


class LineWriter:
    indent_size: int = 4
    lines: list[Line]

    _current_indent: int
    _current_line: str

    def __init__(self) -> None:
        self.lines = []
        self._current_indent = 0
        self._current_line = ""

    def _eat_line(self) -> Line:
        line = Line(self._current_indent, self._current_line)
        self._current_line = ""
        return line

    def indent(self: Self, n=1) -> Self:
        self._current_indent += n
        return self

    def dedent(self: Self, n=1) -> Self:
        if self._current_indent - n < 0:
            raise Exception(f"Tried to dedent passed 0: {self._current_indent=}, {n=}")
        self._current_indent -= n
        return self

    def write(self: Self, *texts: str, join=" ") -> Self:
        self._current_line += join.join(texts)
        return self

    def newline(self: Self, n=1) -> Self:
        for _ in range(n):
            self.lines.append(self._eat_line())
        return self

    def write_line(self: Self, *texts: str) -> Self:
        return self.write(*texts).newline()

    def pad_to_column(self: Self, column: int, padding=" ") -> Self:
        self._current_line += padding * (max(0, column - len(self._current_line)))
        return self

    def compile_lines(self):
        self.newline()
        for line in self.lines:
            yield " " * self.indent_size * line.indent + line.text

    @property
    def text(self):
        return "\n".join(self.compile_lines())
