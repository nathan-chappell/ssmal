from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Callable

from ssmal.lang.ssmalloc.arena import Arena


_proxy_fields = ["proxied_type", "arena", "address", "get_field_offset"]


class ArenaProxy:
    proxied_type: type
    arena: Arena
    address: int
    get_field_offset: Callable[[str], int]

    def __init__(self, type: type, arena: Arena, address: int, get_field_offset: Callable[[str], int]):
        self.proxied_type = type
        self.arena = arena
        self.address = address
        self.get_field_offset = get_field_offset

    def __getattr__(self, name: str) -> int:
        if name in _proxy_fields:
            return object.__getattribute__(self, name)
        field_offset = self.get_field_offset(name)
        if field_offset >= 0:
            field_address = self.address + field_offset
            return int.from_bytes(self.arena.view[field_address : field_address + 4], "little", signed=True)
        else:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: int) -> None:
        global arena
        if name in _proxy_fields:
            return object.__setattr__(self, name, value)
        field_offset = self.get_field_offset(name)
        if field_offset >= 0:
            field_address = self.address + field_offset
            self.arena.view[field_address : field_address + 4] = value.to_bytes(4, "little", signed=True)
        else:
            raise AttributeError(name)

    def __dir__(self) -> list[str]:
        return _proxy_fields + [field.name for field in fields(self.proxied_type)]
