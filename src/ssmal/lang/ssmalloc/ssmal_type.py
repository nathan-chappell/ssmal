from __future__ import annotations
from collections import OrderedDict

from dataclasses import dataclass, fields
from enum import Enum
from itertools import chain
from typing import Generator
from ssmal.lang.ssmalloc.merge_tables import _merge_tables

from ssmal.lang.ssmalloc.override_info import OverrideInfo


@dataclass
class SsmalField:
    name: str
    type: str


@dataclass
class SsmalType:
    base_type: SsmalType | None
    # vtable: tuple[int, ...]
    vtable: tuple[tuple[str, OverrideInfo], ...]
    name: str
    fields: tuple[SsmalField, ...]

    @classmethod
    def offsets(cls) -> dict[str, int]:
        return {"base_type": 0, "vtable": 1, "name": 2, "fields": 3}

    @classmethod
    def from_dataclass(cls, dataclass: type) -> SsmalType:
        bases = dataclass.__bases__
        if len(bases) > 1:
            raise NotImplementedError("Multiple inheritance not supported")
        elif len(bases) == 1 and bases[0] is not object:
            base_type = cls.from_dataclass(bases[0])
            base_method_names = tuple(name for name, _ in base_type.vtable)
        else:
            base_type = None
            base_method_names = tuple()

        method_names: tuple[str, ...] = tuple(
            method_name for method_name, method in dataclass.__dict__.items() if "__" not in method_name and callable(method)
        )

        vtable = _merge_tables(method_names, base_method_names)
        type_name = dataclass.__name__
        _fields = tuple(SsmalField(field.name, field.type.__name__) for field in fields(dataclass))

        return SsmalType(base_type=base_type, vtable=tuple(vtable.items()), name=type_name, fields=_fields)

    @property
    def override_table(self) -> OrderedDict[str, OverrideInfo]:
        return OrderedDict(self.vtable)

    @property
    def strings(self) -> tuple[str]:
        _vtable_names = [method_name for method_name, _ in self.vtable]
        _method_names = [
            f"{self.name}.{method_name}" for method_name, override_info in self.vtable if override_info != OverrideInfo.DoesNotOverride
        ]
        return tuple(chain(_vtable_names, _method_names, [self.name], *[(f.name, f.type) for f in self.fields]))

    def get_implementer(self, virtual_method_name: str) -> SsmalType:
        override_table = self.override_table
        match override_table.get(virtual_method_name, None):
            case None:
                raise KeyError(f"method not in override table: {virtual_method_name=}")
            case (OverrideInfo.DeclaresNew | OverrideInfo.DoesOverride):
                return self
            case (OverrideInfo.DoesNotOverride) if self.base_type is not None:
                return self.base_type.get_implementer(virtual_method_name)
            case _:  # pragma: no cover
                # unreachable...
                raise Exception(f"method not implemented: {virtual_method_name=}")


@dataclass
class SsmalTypeRT:
    base_type_ptr: int
    vtable_ptr: int
    vtable_names_ptr: int
    name_ptr: str
    field_names_ptr: int
