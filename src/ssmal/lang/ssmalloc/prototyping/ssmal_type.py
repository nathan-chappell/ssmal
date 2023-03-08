from __future__ import annotations
from collections import OrderedDict

from dataclasses import dataclass, fields
from itertools import chain
from typing import Any, Callable
from ssmal.lang.ssmalloc.metadata.merge_tables import merge_tables

from ssmal.lang.ssmalloc.metadata.override_type import OverrideType


@dataclass
class SsmalField:
    # offset: int
    name: str
    type: str


@dataclass
class SsmalMethodInfo:
    implementation: Callable
    unqualified_name: str
    defining_type: SsmalType
    override_type: OverrideType
    signature: tuple[SsmalField, ...]
    return_: SsmalField


@dataclass
class SsmalType:
    base_type: SsmalType | None
    # vtable: tuple[int, ...]
    # vtable: tuple[tuple[str, OverrideType], ...]
    vtable: tuple[SsmalMethodInfo, ...]
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
            base_method_names = tuple(method_info.unqualified_name for method_info in base_type.vtable)
        else:
            base_type = None
            base_method_names = tuple()

        methods: OrderedDict[str, Callable] = OrderedDict(
            (method_name, method) for method_name, method in dataclass.__dict__.items() if "__" not in method_name and callable(method)
        )

        method_names: tuple[str, ...] = tuple(methods.keys())

        override_info = merge_tables(method_names, base_method_names)
        type_name = dataclass.__name__
        _fields = tuple(SsmalField(field.name, field.type.__name__) for field in fields(dataclass))
        result = SsmalType(base_type=base_type, vtable=(), name=type_name, fields=_fields)

        vtable = [
            SsmalMethodInfo(implementation=method, unqualified_name=method_name, defining_type=result, override_type=) for method_name, method in methods.items()
        ]

        return SsmalType(base_type=base_type, vtable=tuple(override_info.items()), name=type_name, fields=_fields)

    @property
    def override_table(self) -> OrderedDict[str, OverrideType]:
        return OrderedDict(self.vtable)

    @property
    def strings(self) -> tuple[str]:
        _vtable_names = [method_name for method_name, _ in self.vtable]
        _method_names = [
            f"{self.name}.{method_name}" for method_name, override_info in self.vtable if override_info != OverrideType.DoesNotOverride
        ]
        return tuple(chain(_vtable_names, _method_names, [self.name], *[(f.name, f.type) for f in self.fields]))

    @property
    def symbols(self) -> tuple[str]:
        _symbols = list[str]()
        _symbols.append(self.name)
        _symbols.extend(
            f"{self.name}.{method_name}" for method_name, override_info in self.vtable if override_info != OverrideType.DoesNotOverride
        )
        return (self.name,)

    def get_implementer(self, virtual_method_name: str) -> SsmalType:
        override_table = self.override_table
        match override_table.get(virtual_method_name, None):
            case None:
                raise KeyError(f"method not in override table: {virtual_method_name=}")
            case (OverrideType.DeclaresNew | OverrideType.DoesOverride):
                return self
            case (OverrideType.DoesNotOverride) if self.base_type is not None:
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
