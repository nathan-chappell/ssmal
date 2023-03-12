from collections import OrderedDict
from dataclasses import dataclass
import io
from itertools import chain
from typing import Callable, Generator, Iterable

from ssmal.lang.ssmalloc.metadata.util.arena import Arena
from ssmal.lang.ssmalloc.metadata.util.arena_reader_writer import ArenaReaderWriter
from ssmal.lang.ssmalloc.metadata.util.merge_tables import merge_tables
from ssmal.lang.ssmalloc.prototyping.ssmal_type import SsmalField, SsmalType, OverrideType
from ssmal.lang.ssmalloc.prototyping.string_table import StringTable

POINTER_SIZE = 4


_type_info_offsets = SsmalType.offsets()

SymbolAddress = int
StringTableOffset = int


class SsmalTypeEmbedder:
    arena: Arena
    arena_rw: ArenaReaderWriter
    ssmal_types: list[SsmalType]
    type_info_table_address: int
    # built internally for type and method names
    string_table: StringTable
    string_table_size: int
    # global_string_table_offsets: dict[str, int]
    string_table_address: int = -1
    # for method-implementation lookup
    symbol_table: OrderedDict[SymbolAddress, StringTableOffset]

    TYPE_INFO_TABLE_SYMBOL = "__TYPE_INFO_TABLE"
    TYPE_INFO_SIZE = 5 * POINTER_SIZE

    _builtin_types = [SsmalType(None, (), "str", ()), SsmalType(None, (), "int", ())]

    def __init__(self, arena: Arena, ssmal_types: list[SsmalType], string_table_max_size=0x200) -> None:
        self.arena = arena
        self.arena_rw = ArenaReaderWriter(arena)
        self.ssmal_types = ssmal_types
        self.type_info_table_address = -1
        self.string_table = StringTable(max_size=string_table_max_size)
        self.string_table_size = string_table_max_size
        self.symbol_table = OrderedDict[SymbolAddress, StringTableOffset]()

    @property
    def all_types(self) -> list[SsmalType]:
        return list(*self._builtin_types, *self.ssmal_types)

    def embed(self):
        assert self.string_table_address == -1, "Attempted to embed SsmalTypeInfo more than once."
        self.string_table_address = self.arena.malloc(self.string_table_size)
        assert self.type_info_table_address == -1, "Attempted to embed SsmalTypeInfo more than once."

        self.type_info_table_address = self.arena.malloc(len(self.all_types) * POINTER_SIZE)
        self.symbol_table[self.type_info_table_address] = self.string_table[self.TYPE_INFO_TABLE_SYMBOL]

        for i, ssmal_type in enumerate(self.all_types):
            # string_table_offsets, string_?table_bytes = self.compile_string_table(ssmal_type.strings)
            # self.string_table.add_strings(*ssmal_type.strings)
            # string_table_address = self.arena.embed(string_table_bytes)
            # self.built_string_tables.append((string_table_address, string_table_offsets))

            # def _get_string_address(s: str) -> int:
            #     if s in self.string_table:
            #         return self.string_table_address + self.string_table[s]
            #     raise KeyError(f"string {s=} not in string table")

            type_info_address = self.arena.malloc(self.TYPE_INFO_SIZE)
            self.arena_rw.write_ptr(self.type_info_table_address, type_info_address, offset=i)

            base_type_info_address = self.get_type_info_address(ssmal_type.base_type)
            vtable_address = self.build_vtable(ssmal_type, _get_string_address)
            name_address = _get_string_address(ssmal_type.name)
            fields_address = self.build_field_table(ssmal_type, _get_string_address)

            self.arena_rw.write_ptr(type_info_address, base_type_info_address, offset=_type_info_offsets["base_type"])
            self.arena_rw.write_ptr(type_info_address, vtable_address, offset=_type_info_offsets["vtable"])
            self.arena_rw.write_ptr(type_info_address, name_address, offset=_type_info_offsets["name"])
            self.arena_rw.write_ptr(type_info_address, fields_address, offset=_type_info_offsets["fields"])

    def get_type_name_from_type_info_address(self, type_info_address: int) -> str:
        name_address = self.arena_rw.read_ptr(type_info_address + POINTER_SIZE * _type_info_offsets["name"])
        return self.arena_rw.read_zstr(name_address)

    def get_vtable_names_from_type_info_address(self, type_info_address: int) -> tuple[str, ...]:
        vtable_address = self.arena_rw.read_ptr(type_info_address + POINTER_SIZE * _type_info_offsets["vtable"])
        vtable_count = self.arena_rw.read_ptr(vtable_address)
        names: list[str] = []
        for i in range(vtable_count):
            method_name_address = self.arena_rw.read_ptr(vtable_address, offset=2 * i + 1)
            names.append(self.arena_rw.read_zstr(method_name_address))
        return tuple(names)

    def get_field_names_and_types_from_type_info_address(self, type_info_address: int) -> tuple[tuple[str, str], ...]:
        field_info_address = self.arena_rw.read_ptr(type_info_address + POINTER_SIZE * _type_info_offsets["fields"])
        field_info_count = self.arena_rw.read_ptr(field_info_address)
        _fields: list[tuple[str, str]] = []
        for i in range(field_info_count):
            field_name_address = self.arena_rw.read_ptr(field_info_address, offset=2 * i + 1)
            field_type_address = self.arena_rw.read_ptr(field_info_address, offset=2 * i + 2)
            field_name = self.arena_rw.read_zstr(field_name_address)
            field_type_name = self.get_type_name_from_type_info_address(field_type_address)
            _fields.append((field_name, field_type_name))
        return tuple(_fields)

    def hydrate(self, type_name: str) -> SsmalType:
        type_info_address = self.get_type_info_address_from_name(type_name)

        base_type_info_address = self.arena_rw.read_ptr(type_info_address, offset=_type_info_offsets["base_type"])
        # vtable_address = self.arena_rw.read_ptr(type_info_address, offset=_type_info_offsets["vtable"])
        # name_address = self.arena_rw.read_ptr(type_info_address, offset=_type_info_offsets["name"])
        # fields_address = self.arena_rw.read_ptr(type_info_address, offset=_type_info_offsets["fields"])

        if base_type_info_address != -1:
            base_type_name = self.get_type_name_from_type_info_address(base_type_info_address)
            base_type = self.hydrate(base_type_name)
            base_vtable_names = self.get_vtable_names_from_type_info_address(base_type_info_address)
        else:
            base_vtable_names = tuple()
            base_type = None

        vtable_names = self.get_vtable_names_from_type_info_address(type_info_address)
        _base_vtable_unqualified_names = tuple(n[n.index(".") + 1 :] for n in base_vtable_names)
        _vtable_unqualified_names = tuple(n[n.index(".") + 1 :] for n in vtable_names)
        vtable = merge_tables(_vtable_unqualified_names, _base_vtable_unqualified_names)
        for vtable_name in vtable_names:
            _unqualified = vtable_name[vtable_name.index(".") + 1 :]
            if not vtable_name.startswith(type_name) and vtable[_unqualified] == OverrideType.DoesOverride:
                vtable[_unqualified] = OverrideType.DoesNotOverride

        name = self.get_type_name_from_type_info_address(type_info_address)

        field_names_and_types = self.get_field_names_and_types_from_type_info_address(type_info_address)
        _fields = tuple(SsmalField(name, _type) for name, _type in field_names_and_types)

        return SsmalType(base_type=base_type, vtable=tuple(vtable.items()), name=name, fields=_fields)

    def get_type_info_address_from_name(self, name: str) -> int:
        for i, ssmal_type in enumerate(self.all_types):
            if ssmal_type.name == name:
                ptr_address = self.arena_rw.get_addr(self.type_info_table_address, offset=i)
                return self.arena_rw.read_ptr(ptr_address)
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
            _, method_info = item
            method_name_address = _get_string_address(method_info[0])
            self.arena_rw.write_ptr(vtable_address, method_name_address, offset=2 * i + 1)
            self.arena_rw.write_ptr(vtable_address, method_info[1], offset=2 * i + 2)

        return vtable_address

    def get_vtable_implementations(self, ssmal_type: SsmalType) -> OrderedDict[str, tuple[str, int]]:
        if ssmal_type.name in ("int", "str"):
            return OrderedDict()
        override_table = ssmal_type.override_table
        vtable_implementations = OrderedDict[str, tuple[str, int]]()
        for name in override_table.keys():
            implementer = ssmal_type.get_implementer(name)
            qualified_name = f"{implementer.name}.{name}"
            vtable_implementations[name] = (qualified_name, self.symbol_table[qualified_name])

        return vtable_implementations

    def build_field_table(self, ssmal_type: SsmalType, _get_string_address: Callable[[str], int]) -> int:
        fields_address = self.arena.malloc(POINTER_SIZE * 2 * len(ssmal_type.fields))
        self.arena_rw.write_ptr(fields_address, len(ssmal_type.fields))
        for i, field in enumerate(ssmal_type.fields):
            name_address = _get_string_address(field.name)
            type_address = self.get_type_info_address_from_name(field.type)
            self.arena_rw.write_ptr(fields_address, name_address, offset=2 * i + 1)
            self.arena_rw.write_ptr(fields_address, type_address, offset=2 * i + 2)

        return fields_address
