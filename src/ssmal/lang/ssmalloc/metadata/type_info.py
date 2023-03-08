from __future__ import annotations
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, fields
from enum import Enum
from inspect import signature
import logging
from types import GenericAlias
from typing import Callable, Generic, get_type_hints

from ssmal.lang.ssmalloc.metadata.merge_tables import merge_tables
from ssmal.lang.ssmalloc.metadata.override_type import OverrideType

import ssmal.lang.ssmalloc.internal.System as InternalSystem

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TypeDefinitionStatus(Enum):
    NotSeen = 0
    Defining = 1
    Defined = 2


type_cache: OrderedDict[str, TypeInfo] = OrderedDict()


@dataclass
class TypeInfoBase:
    name: str
    parent: TypeInfoBase | None


@dataclass
class FieldInfo(TypeInfoBase):
    type: TypeInfo
    index: int


@dataclass
class ParameterInfo(TypeInfoBase):
    type: TypeInfo
    index: int


@dataclass
class MethodInfo(TypeInfoBase):
    parameters: list[ParameterInfo]
    return_type: TypeInfo
    code: str | None


@dataclass
class TypeInfo(TypeInfoBase):
    py_type: type
    fields: list[FieldInfo]
    methods: list[MethodInfo]

    def get_method_info(self, name: str) -> MethodInfo | None:
        for method in self.methods:
            if method.name == name:
                return method
        if isinstance(self.parent, TypeInfo):
            return self.parent.get_method_info(name)
        return None

    @classmethod
    def from_py_type(cls, py_type: type) -> TypeInfo:
        if isinstance(py_type, GenericAlias):
            breakpoint()
            ...
        name = py_type.__name__

        log.info(f"{py_type=}")

        result = TypeInfo(name=name, parent=None, py_type=py_type, fields=[], methods=[])

        if name in type_cache:
            return type_cache[name]
        else:
            type_cache[name] = result

        if type(py_type) != type:
            breakpoint()
        if py_type in (int, str) or issubclass(py_type, InternalSystem.BuiltInType):
            return result

        log.info(f"{py_type=}")

        # _fields = tuple(SsmalField(field.name, field.type.__name__) for field in fields(dataclass))
        _fields: list[FieldInfo] = []
        # for i, field in enumerate(fields(py_type)):
        py_type_hints = get_type_hints(py_type)
        for i, field_py_type in enumerate(py_type_hints.values()):
            _fields.append(FieldInfo(name=field_py_type.__name__, parent=result, type=cls.from_py_type(field_py_type), index=i))

        bases = py_type.__bases__
        base_method_names: list[str]
        match bases:
            case type() as T, if T != object:
                base = cls.from_py_type(T)
            case type(),:
                base = None
            case type() as G, type() as T if issubclass(G, Generic):
                base = cls.from_py_type(T)
            case _:
                import ipdb; ipdb.set_trace()
                raise NotImplementedError(f"Unsupported base class declaration: {bases=}, {py_type=}")

        if base is not None:
            base_method_names = [method.name for method in base.methods]
        else:
            base_method_names = []

        class_methods: OrderedDict[str, Callable] = OrderedDict(
            (method_name, method) for method_name, method in dataclass.__dict__.items() if "__" not in method_name and callable(method)
        )
        method_names = list(class_methods.keys())

        override_info = merge_tables(method_names, base_method_names)
        methods: list[MethodInfo] = []

        for method_name, override_type in override_info.items():
            match override_type:
                case OverrideType.DeclaresNew | OverrideType.DoesOverride:
                    parameters: list[ParameterInfo] = []
                    method_hints = get_type_hints(class_methods[method_name])
                    method_signature = signature(class_methods[method_name])

                    for i, parameter in enumerate(method_signature.parameters.values()):
                        if parameter.name == "self":
                            continue
                        parameters.append(
                            ParameterInfo(name=parameter.name, parent=result, type=cls.from_py_type(method_hints[parameter.name]), index=i)
                        )

                    return_type = cls.from_py_type(method_hints["return"])
                    method = MethodInfo(name=method_name, parent=result, parameters=parameters, return_type=return_type, code=None)
                case OverrideType.DoesNotOverride if base is not None and method_name in base_method_names:
                    base_method = base.get_method_info(method_name)
                    assert base_method is not None
                    methods.append(base_method)
                case _:
                    raise Exception(f"No method info available for {method_name} {override_type} {py_type}")

        type_cache[result.name] = result
        return result


if __name__ == "__main__":
    import ssmal.lang.ssmalloc.stdlib as stdlib
    from pprint import pprint

    logging.basicConfig()
    type_info = TypeInfo.from_py_type(stdlib.TypeInfo)
    pprint(type_info)
