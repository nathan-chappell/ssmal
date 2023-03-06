from ssmal.lang.ssmalloc.arena import Arena
from ssmal.lang.ssmalloc.ssmal_type import SsmalType

POINTER_SIZE = 4


class SsmalTypeEmbedder:
    arena: Arena
    ssmal_types: list[SsmalType]
    ssmal_types_table_address: int
    # built internally for type and method names
    string_table: dict[str, int]
    string_table_address: int
    # for method-implementation lookup
    symbol_table: dict[str, int]

    def __init__(self, arena: Arena, ssmal_types: list[SsmalType], symbol_table: dict[str, int]) -> None:
        self.arena = arena
        self.ssmal_types = ssmal_types
        self.ssmal_types_table_address = -1
        self.string_table = {}
        self.string_table_address = -1
        self.symbol_table = symbol_table

    def embed(self):
        assert self.string_table_address == -1, "Attempted to embed SsmalTypeInfo more than once."
        TYPE_INFO_SIZE = 5 * POINTER_SIZE
        self.embed_string_table()
        self.ssmal_types_table_address = self.arena.malloc(len(self.ssmal_types) * POINTER_SIZE)
        for i, ssmal_type in enumerate(self.ssmal_types):
            address = self.arena.malloc(TYPE_INFO_SIZE)
            # get pointers, make tables, ...


    def embed_string_table(self):
        strings = set()
        for ssmal_type in self.ssmal_types:
            strings.add(ssmal_type.name)
            strings.update(ssmal_type.field_names)
            strings.update(ssmal_type.vtable_names)

        _string_list = list(strings)
        _strtable_bytes = b""
        i = 0
        for s in _string_list:
            self.string_table[s] = i
            _strtable_bytes += bytes(s, encoding="ascii") + b"\x00"
            i += len(s) + 1

        self.string_table_address = self.arena.embed(_strtable_bytes)
