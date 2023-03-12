from collections import OrderedDict
import io
from typing import overload


class StringTable:
    max_size: int
    _offset: int
    _map: OrderedDict[str, int]
    _reverse_map: OrderedDict[int, str]

    def __init__(self, max_size: int) -> None:
        self.max_size = max_size
        self._offset = 0
        self._map = OrderedDict[str, int]()
        self._reverse_map = OrderedDict[int, str]()

    def add_strings(self, *strings: str):
        for string in strings:
            _ = self[string]

    def __contains__(self, string: str) -> bool:
        return string in self._map

    @overload
    def __getitem__(self, offset_or_string: int) -> str:
        ...

    @overload
    def __getitem__(self, offset_or_string: str) -> int:
        ...

    def __getitem__(self, offset_or_string: str | int) -> int | str:
        if isinstance(offset_or_string, int):
            offset: int = offset_or_string
            return self._reverse_map[offset]
        else:
            string: str = offset_or_string
            if string in self._map:
                _offset = self._map[string]
            else:
                _offset = self._offset
                self._offset += len(string) + 1
                self._map[string] = _offset
                self._reverse_map[_offset] = string
            if self._offset >= self.max_size:
                raise MemoryError(f"StringTable size exceeded max inserting {string=}")
            return _offset

    def compile(self) -> bytes:
        _bytes = io.BytesIO()
        for k in self._map:
            _bytes.write(bytes(k, "ascii"))
            _bytes.write(b"\x00")
        _bytes.write(b"\x00")
        return _bytes.getvalue()
