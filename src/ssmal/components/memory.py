from io import BufferedIOBase, BytesIO
from typing import Callable, Literal

from ssmal.util.hexdump_bytes import hexdump_bytes
from ssmal.util.interval import Interval

# NOTE:
# MonitoredWrite has a terrible flaw, side-effects from the operation which cause the
# signal won't be commited!
class MonitoredWrite(Exception):
    finish_write_callback: Callable[[], None] | None = None

    def finish_write(self):
        if self.finish_write_callback:
            self.finish_write_callback()
        else:
            raise Exception(f"Failed to finish_write: {self.finish_write_callback=}")


class Memory:
    buffer: BytesIO
    monitored_regions: list[Interval]

    def __init__(self, size=2**8):
        self.buffer = BytesIO(b"\x00" * size)
        self.monitored_regions = []

    def load(self, address: int, size: Literal[1, 2, 4] = 4, signed=True) -> int:
        _bytes = self.load_bytes(address, size)
        return int.from_bytes(_bytes, "little", signed=signed)

    def load_bytes(self, address: int, count=1) -> bytes:
        self.buffer.seek(address, 0)
        return self.buffer.read(count)

    def store(self, address: int, value: int) -> None:
        _bytes = value.to_bytes(4, "little", signed=True)
        self.store_bytes(address, _bytes)

    def store_bytes(self, address: int, _bytes: bytes) -> None:
        def finish_write():
            self.buffer.seek(address, 0)
            self.buffer.write(_bytes)

        write_region = Interval(address, address + len(_bytes))
        for i, monitored_region in enumerate(self.monitored_regions):
            if monitored_region & write_region:
                monitored_write = MonitoredWrite(i, monitored_region, write_region, address, _bytes)
                monitored_write.finish_write_callback = finish_write
                raise monitored_write
        else:
            finish_write()

    def dump(self):  # pragma: no cover
        print("\n".join(hexdump_bytes(self.buffer.getvalue())))

    def monitor(self, start: int, end: int):
        self.monitored_regions.append(Interval(start, end))
