from __future__ import annotations
from collections import OrderedDict

from dataclasses import dataclass, fields
from enum import Enum
from itertools import chain
from typing import Generator


@dataclass
class SsmalField:
    name: str
    type: str


class OverrideInfo(Enum):
    DoesNotOverride = 1
    DoesOverride = 2
    DeclaresNew = 3


@dataclass
class SsmalType:
    base_type: SsmalType | None
    # vtable: tuple[int, ...]
    vtable_names: tuple[str, ...]
    name: str
    fields: tuple[SsmalField, ...]

    @classmethod
    def offsets(cls) -> dict[str, int]:
        return {
            'base_type': 0,
            'vtable': 1,
            'name': 2,
            'fields': 3,
        }

    @classmethod
    def from_dataclass(cls, dataclass: type) -> SsmalType:
        bases = dataclass.__bases__
        if len(bases) > 1:
            raise NotImplementedError("Multiple inheritance not supported")
        elif len(bases) == 1 and bases[0] is not object:
            base_type = cls.from_dataclass(bases[0])
        else:
            base_type = None

        vtable_names: tuple[str, ...] = tuple(
            method_name for method_name, method in dataclass.__dict__.items() if "__" not in method_name and callable(method)
        )
        type_name = dataclass.__name__
        _fields = tuple(SsmalField(field.name, field.type.__name__) for field in fields(dataclass))

        return SsmalType(base_type=base_type, vtable_names=vtable_names, name=type_name, fields=_fields)

    @property
    def override_table(self) -> OrderedDict[str, OverrideInfo]:
        result = OrderedDict[str, OverrideInfo]()
        if self.base_type is not None:
            for name in self.base_type.vtable_names:
                if name in self.vtable_names:
                    result[name] = OverrideInfo.DoesOverride
                else:
                    result[name] = OverrideInfo.DoesNotOverride
        for name in self.vtable_names:
            if name in result:
                continue
            else:
                result[name] = OverrideInfo.DeclaresNew
        return result

    @property
    def strings(self) -> tuple[str]:
        return tuple(chain(self.vtable_names, [self.name], *[(f.name, f.type) for f in self.fields]))

    def get_implementer(self, virtual_method_name: str) -> SsmalType:
        override_table = self.override_table
        match override_table.get(virtual_method_name, None):
            case None:
                raise KeyError(f"method not in override table: {virtual_method_name=}")
            case (OverrideInfo.DeclaresNew | OverrideInfo.DoesOverride):
                return self
            case (OverrideInfo.DoesNotOverride) if self.base_type is not None:
                return self.base_type.get_implementer(virtual_method_name)
            case _: # pragma: no cover
                # unreachable...
                raise Exception(f"method not implemented: {virtual_method_name=}")


@dataclass
class SsmalTypeRT:
    base_type_ptr: int
    vtable_ptr: int
    vtable_names_ptr: int
    name_ptr: str
    field_names_ptr: int
