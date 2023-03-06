from collections import OrderedDict
from dataclasses import dataclass
import io
from typing import Callable, Generator

from ssmal.lang.ssmalloc.arena import Arena
from ssmal.lang.ssmalloc.arena_reader_writer import ArenaReaderWriter
from ssmal.lang.ssmalloc.ssmal_type import SsmalField, SsmalType, OverrideInfo

POINTER_SIZE = 4



class SsmalTypeEmbedder:
    arena: Arena
    arena_rw: ArenaReaderWriter
    ssmal_types: list[SsmalType]
    ssmal_types_table_address: int
    # built internally for type and method names
    string_table: dict[str, int]
    string_table_address: int
    # for method-implementation lookup
    symbol_table: dict[str, int]

    def __init__(self, arena: Arena, ssmal_types: list[SsmalType], symbol_table: dict[str, int]) -> None:
        self.arena = arena
        self.arena_rw = ArenaReaderWriter(arena)
        self.ssmal_types = ssmal_types
        self.ssmal_types_table_address = -1
        self.string_table = {}
        self.string_table_address = -1
        self.symbol_table = symbol_table

    def embed(self):
        assert self.string_table_address == -1, "Attempted to embed SsmalTypeInfo more than once."
        TYPE_INFO_SIZE = 5 * POINTER_SIZE

        self.ssmal_types_table_address = self.arena.malloc(len(self.ssmal_types) * POINTER_SIZE)
        _type_info_offsets = SsmalType.offsets()

        for i, ssmal_type in enumerate(self.ssmal_types):
            string_table_offsets, string_table_bytes = self.compile_string_table(ssmal_type.strings)
            string_table_address = self.arena.embed(string_table_bytes)

            def _get_string_address(s: str) -> int:
                return string_table_address + string_table_offsets[s]

            type_info_address = self.arena.malloc(TYPE_INFO_SIZE)
            self.arena_rw.write_ptr(self.ssmal_types_table_address, type_info_address, offset=i)

            base_type_info_address = self.get_type_info_address(ssmal_type.base_type)
            vtable_address = self.build_vtable(ssmal_type, _get_string_address)
            name_address = _get_string_address(ssmal_type.name)
            fields_address = self.build_field_table(ssmal_type, _get_string_address)

            self.arena_rw.write_ptr(type_info_address, base_type_info_address, offset=_type_info_offsets["base_type"])
            self.arena_rw.write_ptr(type_info_address, vtable_address, offset=_type_info_offsets["vtable"])
            self.arena_rw.write_ptr(type_info_address, name_address, offset=_type_info_offsets["name"])
            self.arena_rw.write_ptr(type_info_address, fields_address, offset=_type_info_offsets["fields"])

    def hydrate(self, type_name: str) -> SsmalType:
        _type_info_offsets = SsmalType.offsets()
        type_info_address = self.get_type_info_address_from_name(type_name)

        base_type_info_address = self.arena_rw.read_ptr(type_info_address, offset=_type_info_offsets["base_type"])
        vtable_address = self.arena_rw.read_ptr(type_info_address, offset=_type_info_offsets["vtable"])
        name_address = self.arena_rw.read_ptr(type_info_address, offset=_type_info_offsets["name"])
        fields_address = self.arena_rw.read_ptr(type_info_address, offset=_type_info_offsets["fields"])

        base_type_name = self.arena_rw.read_zstr(base_type_info_address + POINTER_SIZE * _type_info_offsets["name"])
        base_type = self.hydrate(base_type_name)

        vtable_names: list[str] = []
        vtable_size = self.arena_rw.read_ptr(vtable_address)
        for i in range(vtable_size):
            method_name_address = self.arena_rw.read_ptr(self.arena_rw.get_addr(vtable_address, offset=2 * i + 1))
            vtable_names.append(self.arena_rw.read_zstr(method_name_address))

        name = self.arena_rw.read_zstr(name_address)

        _fields: list[SsmalField] = []
        fields_size = self.arena_rw.read_ptr(fields_address)
        for i in range(fields_size):
            field_name_address = self.arena_rw.read_ptr(self.arena_rw.get_addr(fields_address, offset=2 * i + 1))
            field_type_address = self.arena_rw.read_ptr(self.arena_rw.get_addr(fields_address, offset=2 * i + 2))
            field_name = self.arena_rw.read_zstr(field_name_address)
            field_type = self.arena_rw.read_zstr(field_type_address)
            _fields.append(SsmalField(field_name, field_type))

        return SsmalType(base_type=base_type, vtable_names=tuple(vtable_names), name=name, fields=tuple(_fields))

    def compile_string_table(self, strings: tuple[str]) -> tuple[OrderedDict[str, int], bytes]:
        buffer = io.BytesIO()
        offsets = OrderedDict[str, int]()
        for string in strings:
            if string in offsets:
                continue
            else:
                offsets[string] = buffer.tell()
            buffer.write(bytes(string, encoding="ascii"))
            buffer.write(b"\x00")
        buffer.write(b"\x00")
        return offsets, buffer.getvalue()

    def get_type_info_address_from_name(self, name: str) -> int:
        if name == "int":
            return -2
        if name == "str":
            return -3
        for i, ssmal_type in enumerate(self.ssmal_types):
            if ssmal_type.name == name:
                return self.arena_rw.get_addr(self.ssmal_types_table_address, i)
        else:
            return -1

    def get_type_info_address(self, type_info: SsmalType | None) -> int:
        if type_info is None:
            return -1
        else:
            return self.get_type_info_address_from_name(type_info.name)

    def build_vtable(self, ssmal_type: SsmalType, _get_string_address: Callable[[str], int]) -> int:
        vtable_implementations = self.get_vtable_implementations(ssmal_type)
        vtable_address = self.arena.malloc(1 + POINTER_SIZE * 2 * len(vtable_implementations))
        self.arena_rw.write_ptr(vtable_address, len(vtable_implementations))
        for i, item in enumerate(vtable_implementations.items()):
            method_name, method_address = item
            method_name_address = _get_string_address(method_name)
            self.arena_rw.write_ptr(vtable_address, method_name_address, offset=2 * i + 1)
            self.arena_rw.write_ptr(vtable_address, method_address, offset=2 * i + 2)

        return vtable_address

    def get_vtable_implementations(self, ssmal_type: SsmalType) -> OrderedDict[str, int]:
        override_table = ssmal_type.override_table
        vtable_implementations = OrderedDict[str, int]()
        for name in override_table.keys():
            implementer = ssmal_type.get_implementer(name)
            qualified_name = f"{implementer.name}.{name}"
            vtable_implementations[name] = self.symbol_table[qualified_name]

        return vtable_implementations

    def build_field_table(self, ssmal_type: SsmalType, _get_string_address: Callable[[str], int]) -> int:
        fields_address = self.arena.malloc(POINTER_SIZE * 2 * len(ssmal_type.fields))
        self.arena_rw.write_ptr(fields_address, len(ssmal_type.fields))
        for i, field in enumerate(ssmal_type.fields):
            name_address = _get_string_address(field.name)
            type_address = self.get_type_info_address_from_name(field.name)
            self.arena_rw.write_ptr(fields_address, name_address, offset=2 * i + 1)
            self.arena_rw.write_ptr(fields_address, type_address, offset=2 * i + 2)

        return fields_address
