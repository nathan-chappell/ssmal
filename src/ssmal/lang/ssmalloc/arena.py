class Arena:
    index: int = 0
    view: memoryview

    def __init__(self, view: memoryview) -> None:
        self.view = view

    @property
    def size(self) -> int:
        return len(self.view)

    def malloc(self, size: int) -> int:
        if self.index + size >= self.size:
            raise MemoryError(f"Failed to allocate {size=} bytes: {self.index=}")
        address = self.index
        self.index += size
        return address


default_arena = Arena(memoryview(bytearray(0x1000)))
