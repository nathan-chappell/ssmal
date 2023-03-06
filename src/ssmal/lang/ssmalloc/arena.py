class Arena:
    index: int = 0
    view: memoryview

    ALIGNMENT = 0x20

    def __init__(self, view: memoryview) -> None:
        self.view = view

    @property
    def size(self) -> int:
        return len(self.view)

    def _align(self):
        self.index += self.ALIGNMENT - (self.index % self.ALIGNMENT)
    
    def malloc(self, size: int) -> int:
        if self.index + size >= self.size:
            raise MemoryError(f"Failed to allocate {size=} bytes: {self.index=}")
        address = self.index
        self.index += size
        self._align()
        return address
    
    def embed(self, _bytes: bytes) -> int:
        address = self.malloc(len(_bytes))
        self.view[address: address + len(_bytes)] = _bytes
        return address


default_arena = Arena(memoryview(bytearray(0x1000)))
