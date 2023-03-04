from io import BufferedIOBase, BytesIO
from typing import Literal

from ssmal.util.hexdump_bytes import hexdump_bytes


def _intersects(r1: tuple[int, int], r2: tuple[int, int]) -> bool:
    r1_is_superset = r1[0] < r2[0] and r2[1] < r1[1]
    r10_in_r2 = r2[0] < r1[0] and r1[0] < r2[1]
    r11_in_r2 = r2[0] < r1[1] and r1[1] < r2[1]
    return r1_is_superset or r10_in_r2 or r11_in_r2


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
        _bytes = value.to_bytes(4, "little", signed=True)
        self.store_bytes(address, _bytes)

    def store_bytes(self, address: int, _bytes: bytes) -> None:
        if region := self.check_if_monitored((address, address + len(_bytes))):
            self.handle_write_to_monitored_region(address, _bytes, region)
        self.buffer.seek(address, 0)
        self.buffer.write(_bytes)

    def dump(self, start=0, end=0x200):  # pragma: no cover
        count = end - start
        assert 0 <= count
        print("\n".join(hexdump_bytes(self.load_bytes(start, count), start)))

    def watch_region(self, region: tuple[int, int]):
        self.monitored_regions.append(region)

    def check_if_monitored(self, region: tuple[int, int]) -> tuple[int, int] | None:
        for monitored_region in self.monitored_regions:
            if _intersects(region, monitored_region):
                return monitored_region

    def handle_write_to_monitored_region(self, address: int, _bytes: bytes, region: tuple[int, int]):
        # fmt: off
        import ipdb; ipdb.set_trace() # pragma: no cover
