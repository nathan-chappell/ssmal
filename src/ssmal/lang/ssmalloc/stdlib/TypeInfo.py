from __future__ import annotations
from ssmal.lang.ssmalloc.internal.System import *
from ssmal.lang.ssmalloc.stdlib import *


@dataclass
class TypeInfoBase:
    name: String
    parent: TypeInfoBase

    def foo(self, bar: Int) -> Int:
        ...

    def print(self, indent: Int) -> Int:
        self.foo(indent)
        i: Int = indent
        j: Int = i - Int(3) + Int(1)
        z: str = "foobar"
        if i and j:
            ...
        elif i or j:
            ...
        else:
            ...
        # print(" ", indent)
        # print(i, indent)
        # print(z, indent)
        # print("<TypeInfo ")
        # print(self.name)
        # print(" -> ")
        print(self.parent.name)
        print(">")
        return 1
        



@dataclass
class FieldInfo(TypeInfoBase):
    type: TypeInfo
    index: Int


@dataclass
class ParameterInfo(TypeInfoBase):
    type: TypeInfo
    index: Int


@dataclass
class MethodInfo(TypeInfoBase):
    parameters: ArrayBase[ParameterInfo]
    return_type: TypeInfo
    code: Ptr

    def get_parameter_info(self, name: String) -> ParameterInfo | Null:
        for parameter in self.parameters:
            if parameter.name == name:
                return parameter
        return Null()


@dataclass
class TypeInfo(TypeInfoBase):
    fields: ArrayBase[FieldInfo]
    methods: ArrayBase[MethodInfo]

    def get_field_info(self, name: String) -> FieldInfo | Null:
        for field in self.fields:
            if field.name == name:
                return field
        return Null()

    def get_method_info(self, name: String) -> MethodInfo | Null:
        for method in self.methods:
            if method.name == name:
                return method
        return Null()
