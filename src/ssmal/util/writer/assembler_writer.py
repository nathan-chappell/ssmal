from typing import TypeVar
from ssmal.util.writer.line_writer import LineWriter

Self = TypeVar("Self", bound="AssemblerWriter")


class AssemblerWriter(LineWriter):
    def __init__(self) -> None:
        super().__init__()

    def label(self: Self, name: str) -> Self:
        return self.write(f"{name}:")

    def comment(self: Self, _comment: str) -> Self:
        return self.pad_to_column(30).write_line("; ", _comment)

    def align(self: Self) -> Self:
        return self.newline().write_line(".align")
