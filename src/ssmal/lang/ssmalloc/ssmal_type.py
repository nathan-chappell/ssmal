from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SsmalType:
    base_type: SsmalType | None
    vtable_count: int
    vtable: tuple[int, ...]
    vtable_names: tuple[str, ...]
    name: str
    field_count: int
    field_names: tuple[str, ...]
