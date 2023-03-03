from io import BufferedIOBase, BytesIO
from typing import Literal

from ssmal.util.hexdump_bytes import hexdump_bytes


class Memory:
    buffer: BufferedIOBase
    monitored_regions: list[tuple[int, int]]

    def __init__(self, size=2**8):
        self.buffer = BytesIO(b"\x00" * size)
        self.monitored_regions = []

    def load(self, address: int, size: Literal[1, 2, 4] = 4) -> int:
        _bytes = self.load_bytes(address, size)
        return int.from_bytes(_bytes, "little", signed=True)

    def load_bytes(self, address: int, count=1) -> bytes:
        self.buffer.seek(address, 0)
        return self.buffer.read(count)

    def store(self, address: int, value: int) -> None:
        if self.check_if_monitored(address):
            import ipdb; ipdb.set_trace()
        _bytes = value.to_bytes(4, "little", signed=True)
        self.store_bytes(address, _bytes)

    def store_bytes(self, address: int, _bytes: bytes) -> None:
        if self.check_if_monitored(address):
            import ipdb; ipdb.set_trace()
        self.buffer.seek(address, 0)
        self.buffer.write(_bytes)

    def dump(self, start=0, end=0x200):
        count = end - start
        assert 0 <= count
        print("\n".join(hexdump_bytes(self.load_bytes(start, count), start)))

    def watch_region(self, start: int, end: int):
        self.monitored_regions.append((start, end))

    def check_if_monitored(self, address: int) -> bool:
        return any([start <= address < end for start, end in self.monitored_regions])
