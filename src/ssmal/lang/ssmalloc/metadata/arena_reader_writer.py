from dataclasses import dataclass
from typing import Generator

from ssmal.lang.ssmalloc.metadata.arena import Arena

POINTER_SIZE = 4


@dataclass
class ArenaReaderWriter:
    arena: Arena

    def get_addr(self, base_address: int, offset: int = 0) -> int:
        return base_address + offset * POINTER_SIZE

    def get_view(self, start: int, size: int) -> memoryview:
        return self.arena.view[start : start + size]

    def read_zstr(self, address: int) -> str:
        zstr: str = ""
        while self.arena.view[address] != 0:
            zstr += str(self.arena.view[address].to_bytes(1, "little", signed=False), encoding="ascii")
            address += 1
        return zstr

    def read_zstr_table(self, address: int) -> Generator[str, None, None]:
        while self.arena.view[address] != 0:
            zstr = self.read_zstr(address)
            yield zstr
            address += len(zstr) + 1

    def read_ptr(self, base_address: int, *, offset: int = 0) -> int:
        return int.from_bytes(self.get_view(base_address + offset * POINTER_SIZE, 4), "little", signed=True)

    def write_ptr(self, base_address: int, value: int, *, offset: int = 0):
        self.get_view(base_address + offset * POINTER_SIZE, 4)[:4] = value.to_bytes(4, "little", signed=True)
