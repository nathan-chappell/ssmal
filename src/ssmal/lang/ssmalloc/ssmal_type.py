from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SsmalType:
    base_type: SsmalType | None
    vtable: tuple[int, ...]
    vtable_names: tuple[str, ...]
    name: str
    field_names: tuple[str, ...]


@dataclass
class SsmalTypeRT:
    base_type_ptr: int
    vtable_ptr: int
    vtable_names_ptr: int
    name_ptr: str
    field_names_ptr: int
