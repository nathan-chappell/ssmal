from dataclasses import fields
from ssmal.lang.ssmalloc.ssmal_type import SsmalType
from ssmal.lang.ssmalloc.arena import Arena

POINTER_SIZE = 4


class SsmalRttiManager:
    arena: Arena
    loaded_types: list[str]
    max_types: int
    method_impl_map: dict[str, int]
    type_heap: int = -1
    type_cache: dict[str, SsmalType]

    def __init__(self, arena: Arena, max_types: int = 10):
        self.arena = arena
        self.loaded_types = []
        self.max_types = max_types
        self.method_impl_map = {}
        self.type_heap = arena.malloc(POINTER_SIZE * self.max_types)
        self.type_cache = {}

    def _heap_addr(self, index: int) -> int:
        return self.type_heap + POINTER_SIZE * index

    def _heap_view(self, index: int) -> memoryview:
        _p = self._heap_addr(index)
        return self.arena.view[_p : _p + POINTER_SIZE]

    def _read_zstr(self, address: int) -> str:
        zstr = ""
        i = address
        while self.arena.view[i] != 0:
            zstr += str(self.arena.view[i].to_bytes(1, "little", signed=False), encoding="ascii")
            i += 1
        return zstr

    def from_type(self, type: type) -> SsmalType:
        type_name = type.__name__
        if type_name not in self.type_cache:
            bases = type.__bases__
            if len(bases) > 1:
                raise NotImplementedError("Multiple inheritance not supported")
            elif len(bases) == 1 and bases[0] is not object:
                base_type = self.from_type(bases[0])
            else:
                base_type = None

            vtable, vtable_names = self._construct_vtable(type, base_type)
            field_names = tuple(f.name for f in fields(type))

            self.type_cache[type_name] = SsmalType(
                base_type=base_type, vtable=vtable, vtable_names=vtable_names, name=type_name, field_names=field_names
            )

        return self.type_cache[type_name]

    def compile_type(self, ssmal_type: SsmalType) -> bytes:
        if ssmal_type.base_type is not None:
            base_type_index = self.loaded_types.index(ssmal_type.base_type.name)
            base_type_address = self._read_int(base_type_index)
        else:
            base_type_address = -1
        _base_type_bytes = base_type_address.to_bytes(4, "little", signed=True)
        _vtable_count_bytes = ssmal_type.vtable_count.to_bytes(4, "little", signed=True)
        _vtable_bytes = b"".join(pointer.to_bytes(4, "little", signed=True) for pointer in ssmal_type.vtable)
        _name_bytes = bytes(ssmal_type.name, "ascii") + b"\x00"
        _field_count_bytes = (ssmal_type.field_count).to_bytes(4, "little", signed=True)
        _field_name_bytes = b"\x00".join(bytes(field_name, "ascii") for field_name in ssmal_type.field_names) + b"\x00\x00"
        # fmt: off
        return (
            _base_type_bytes
            + _vtable_count_bytes
            + _vtable_bytes
            + _name_bytes
            + _field_count_bytes
            + _field_name_bytes
        )
        # fmt: on

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

    def _read_int(self, address: int) -> int:
        return int.from_bytes(self.arena.view[address : address + POINTER_SIZE], "little", signed=True)

    def _read_name_list(self, address: int, count: int) -> tuple[str, ...]:
        names: list[str] = []
        for _ in range(count):
            _field_name_address = address + sum(len(field_name) + 1 for field_name in names)
            names.append(self._read_zstr(_field_name_address))
        return tuple(names)

    def load_type_from_address(self, type_address: int) -> SsmalType:
        base_address = int.from_bytes(self.arena.view[type_address : type_address + POINTER_SIZE], "little", signed=True)
        if base_address >= 0:
            base_type = self.load_type_from_address(base_address)
        else:
            base_type = None

        vtable_count = self._read_int(type_address + POINTER_SIZE)

        vtable: list[int] = []
        for i in range(vtable_count):
            vtable.append(self._read_int(type_address + 2 * POINTER_SIZE + i * POINTER_SIZE))

        vtable_names: tuple[str] = self._read_name_list(type_address + 2 * POINTER_SIZE + vtable_count * POINTER_SIZE, len(vtable))

        _HERE = (
            type_address + 2 * POINTER_SIZE + vtable_count * POINTER_SIZE + sum(len(vtable_name) + 1 for vtable_name in vtable_names) + 1
        )
        name = self._read_zstr(_HERE)

        field_count = self._read_int(_HERE + len(name) + 1)
        field_names: tuple[str] = self._read_name_list(_HERE + len(name) + 1 + POINTER_SIZE, field_count)

        return SsmalType(
            base_type=base_type,
            vtable_count=vtable_count,
            vtable=tuple(vtable),
            vtable_names=vtable_names,
            name=name,
            field_count=field_count,
            field_names=field_names,
        )

    def load_type(self, type_name: str) -> SsmalType:
        type_index = self.loaded_types.index(type_name)
        type_address = int.from_bytes(self._heap_view(type_index), "little", signed=True)
        return self.load_type_from_address(type_address)

    def create_object(self, type_name: str) -> int:
        ...
