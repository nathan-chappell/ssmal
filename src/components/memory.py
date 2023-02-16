from io import BufferedIOBase, BytesIO

class Memory:
    buffer: BufferedIOBase

    def __init__(self, size=2**8):
        self.buffer = BytesIO(b'\x00'*size)

    def load(self, address: int) -> int:
        self.buffer.seek(address)
        _bytes = self.buffer.read(4)
        return int.from_bytes(_bytes, 'little')
    
    def store(self, address: int, value: int) -> None:
        _bytes = value.to_bytes(4, 'little')
        self.buffer.seek(address)
        self.buffer.write(_bytes)