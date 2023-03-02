from io import BufferedIOBase, BytesIO
from typing import Literal


class Memory:
    buffer: BufferedIOBase

    def __init__(self, size=2**8):
        self.buffer = BytesIO(b"\x00" * size)

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
        self.buffer.seek(address, 0)
        self.buffer.write(_bytes)
