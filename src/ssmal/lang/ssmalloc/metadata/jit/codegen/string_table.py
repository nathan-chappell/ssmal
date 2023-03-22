from collections import OrderedDict
import io
import re
from typing import NewType, overload
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_internals import CompilerInternals

from ssmal.util.writer.line_writer import LineWriter

Symbol = NewType("Symbol", str)


class StringTable:
    str_to_symbol: OrderedDict[str, Symbol]
    ci = CompilerInternals()

    def __init__(self) -> None:
        self.str_to_symbol = OrderedDict[str, Symbol]()

    def _make_symbol(self, string: str) -> Symbol:
        i = len(self.str_to_symbol)
        fragment = "".join(re.split(r"\W", string))[:0x0C]
        return Symbol(f"z{i:03}_{fragment}")

    def add(self, string: str):
        if string not in self.str_to_symbol:
            self.str_to_symbol[string] = self._make_symbol(string)

    def __contains__(self, string: str) -> bool:
        return string in self.str_to_symbol

    def __getitem__(self, string: str) -> Symbol:
        self.add(string)
        return self.str_to_symbol[string]

    def compile(self, line_writer: LineWriter) -> None:
        ci = self.ci
        for str_, symbol in self.str_to_symbol.items():
            line_writer.write_line(ci.MARK_LABEL(symbol), ci.ZSTR(str_))
