from ssmal.lang.ssmalloc.ssmal_type import SsmalType, FIELD_SIZE
from ssmal.lang.ssmalloc.arena import Arena


class SsmalRttiManager:
    arena: Arena
    loaded_types: list[str]
    max_types: int
    type_heap: int = -1

    def __init__(self, arena: Arena, max_types: int = 10):
        self.arena = arena
        self.loaded_types = []
        self.max_types = max_types
        self.type_heap = arena.malloc(FIELD_SIZE * self.max_types)

    def _heap_addr(self, index: int) -> int:
        return self.type_heap + FIELD_SIZE * index

    def _heap_view(self, index: int) -> memoryview:
        _p = self._heap_addr(index)
        return self.arena.view[_p : _p + FIELD_SIZE]

    def _read_zstr(self, address: int) -> str:
        zstr = ""
        i = address
        while self.arena.view[i] != 0:
            zstr += str(self.arena.view[i].to_bytes(1, "little", signed=False), encoding="ascii")
            i += 1
        return zstr

    def compile_type(self, ssmal_type: SsmalType) -> bytes:
        if ssmal_type.base_type is not None:
            base_type_index = self.loaded_types.index(ssmal_type.base_type.name)
            base_type_address = int.from_bytes(self._heap_view(base_type_index), "little", signed=True)
        else:
            base_type_address = -1
        _base_type_bytes = (base_type_address).to_bytes(4, "little", signed=True)
        _field_count_bytes = (ssmal_type.field_count).to_bytes(4, "little", signed=True)
        _name_bytes = bytes(ssmal_type.name, "ascii") + b"\x00"
        _field_name_bytes = b"\x00".join(bytes(field_name, "ascii") for field_name in ssmal_type.field_names) + b"\x00\x00"
        return _base_type_bytes + _field_count_bytes + _name_bytes + _field_name_bytes

    def store_type(self, ssmal_type: SsmalType):
        if len(self.loaded_types) == self.max_types:
            raise Exception(f"Max types reached {self.max_types} while loading {ssmal_type}")
        if ssmal_type.name in self.loaded_types:
            raise Exception(f"Double type load while loading {ssmal_type}")
        _type_bytes = self.compile_type(ssmal_type)
        address = self.arena.malloc(len(_type_bytes))
        self._heap_view(len(self.loaded_types))[0:4] = address.to_bytes(4, "little", signed=True)
        self.arena.view[address : address + len(_type_bytes)] = _type_bytes
        self.loaded_types.append(ssmal_type.name)

    def load_type(self, type_name: str) -> SsmalType:
        type_index = self.loaded_types.index(type_name)
        type_address = int.from_bytes(self._heap_view(type_index), "little", signed=True)
        _base_address = int.from_bytes(self.arena.view[type_address : type_address + FIELD_SIZE], "little", signed=True)
        if _base_address != -1:
            _base_name = self._read_zstr(_base_address + 2 * FIELD_SIZE)
            base_type = self.load_type(_base_name)
        else:
            base_type = None

        _field_count = int.from_bytes(self.arena.view[type_address + FIELD_SIZE : type_address + 2 * FIELD_SIZE], "little", signed=True)
        address = type_address + 2 * FIELD_SIZE
        _name = self._read_zstr(address)
        address += len(_name) + 1
        _field_names: list[str] = []
        while self.arena.view[address] != 0 and len(_field_names) < _field_count:
            _field_names.append(self._read_zstr(address))
            address += len(_field_names[-1]) + 1
        return SsmalType(base_type, _field_count, _name, tuple(_field_names))

    def create_object(self, type_name: str) -> int:
        ...
