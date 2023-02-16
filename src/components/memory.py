import typing as T
from io import BufferedIOBase, BytesIO

class Memory:
    buffer: BufferedIOBase

    def __init__(self, size=2**8):
        self.buffer = BytesIO(b'\x00'*size)

    def load(self, address: int, size: T.Literal[1,2,4] = 4) -> int:
        self.buffer.seek(address, 0)
        _bytes = self.buffer.read(size)
        return int.from_bytes(_bytes, 'little', signed=True)
    
    def load_bytes(self, address: int, count=1) -> bytes:
        self.buffer.seek(address, 0)
        return self.buffer.read(count)
    
    def store(self, address: int, value: int) -> None:
        _bytes = value.to_bytes(4, 'little', signed=True)
        self.buffer.seek(address, 0)
        self.buffer.write(_bytes)