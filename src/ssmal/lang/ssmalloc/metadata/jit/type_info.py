from __future__ import annotations
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, fields
from enum import Enum
from inspect import signature
import logging
from types import GenericAlias
from typing import Callable, Generic, get_type_hints

from ssmal.lang.ssmalloc.metadata.util.merge_tables import merge_tables
from ssmal.lang.ssmalloc.metadata.util.override_type import OverrideType

# import ssmal.lang.ssmalloc.metadata.System as InternalSystem

log = logging.getLogger(__name__)


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
    assembly_code: str | None
    method: Callable


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

    def get_field_info(self, name: str) -> FieldInfo | None:
        for field in self.fields:
            if field.name == name:
                return field
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

        if py_type in (int, str) or name == "ArrayBase":
            return result

        log.info(f"{py_type=}")

        py_type_hints = get_type_hints(py_type)
        for i, type_hint in enumerate(py_type_hints.items()):
            result.fields.append(FieldInfo(name=type_hint[0], parent=result, type=cls.from_py_type(type_hint[1]), index=i))

        bases = py_type.__bases__
        base_method_names: list[str]
        match bases:
            case type() as T, if T != object:
                result.parent = cls.from_py_type(T)
            case type(),:
                result.parent = None
            case type() as G, type() as T if issubclass(G, Generic):
                result.parent = cls.from_py_type(T)
            case _:
                import ipdb

                ipdb.set_trace()
                raise NotImplementedError(f"Unsupported base class declaration: {bases=}, {py_type=}")

        if result.parent is not None:
            base_method_names = [method.name for method in result.parent.methods]
        else:
            base_method_names = []

        class_methods: OrderedDict[str, Callable] = OrderedDict(
            (method_name, method) for method_name, method in dataclass.__dict__.items() if "__" not in method_name and callable(method)
        )
        method_names = list(class_methods.keys())

        override_info = merge_tables(method_names, base_method_names)

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
                    result.methods.append(
                        MethodInfo(
                            name=method_name,
                            parent=result,
                            parameters=parameters,
                            return_type=return_type,
                            assembly_code=None,
                            method=class_methods[method_name],
                        )
                    )
                case OverrideType.DoesNotOverride if result.parent is not None and method_name in base_method_names:
                    base_method = result.parent.get_method_info(method_name)
                    assert base_method is not None
                    result.methods.append(base_method)
                case _:
                    raise Exception(f"No method info available for {method_name} {override_type} {py_type}")

        type_cache[result.name] = result
        return result


# if __name__ == "__main__":
#     import ssmal.lang.ssmalloc.stdlib as stdlib
#     from pprint import pprint

#     logging.basicConfig()
#     log.setLevel(logging.DEBUG)
#     type_info: TypeInfo = TypeInfo.from_py_type(stdlib.TypeInfo)
#     pprint(type_info)
