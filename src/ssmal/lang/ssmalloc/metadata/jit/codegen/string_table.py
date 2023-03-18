from collections import OrderedDict
import io
import re
from typing import NewType, overload

from ssmal.util.writer.line_writer import LineWriter

Symbol = NewType('Symbol', str)

class StringTable:
    str_to_symbol: OrderedDict[str, Symbol]

    def __init__(self, max_size: int) -> None:
        self.str_to_symbol = OrderedDict[str, Symbol]()
    
    def _make_symbol(self, string: str) -> Symbol:
        i = len(self.str_to_symbol)
        fragment = ''.join(re.split(r'\W', string))[:0x0c]
        return Symbol(f'z{i:03}_{fragment}')

    def add(self, string: str):
        if string not in self.str_to_symbol:
            self.str_to_symbol[string] = self._make_symbol(string)
    
    def __contains__(self, string: str) -> bool:
        return string in self.str_to_symbol

    def __getitem__(self, string: str) -> Symbol:
        self.add(string)
        return self.str_to_symbol[string]

    def compile(self, line_writer: LineWriter) -> str:
        ...
