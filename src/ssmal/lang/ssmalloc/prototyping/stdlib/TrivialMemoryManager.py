from ssmal.lang.ssmalloc.internal.System import *


@dataclass
class TrivialMemoryManager:
    """Type system proof-of-concept"""

    heap: IntArray
    index: Int

    def __init__(self, size: Int):
        self.index = Int(0)
        self.heap = IntArray(size)

    def malloc(self, size: Int) -> Ptr:
        result: Ptr = Ptr(0)
        size += self.index
        if self.heap.size <= size:
            result = Ptr(-1)
        else:
            result += self.index
            self.index = size
        return result
