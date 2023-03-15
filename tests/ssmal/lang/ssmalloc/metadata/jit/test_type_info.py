from dataclasses import dataclass

import pytest

from ssmal.lang.ssmalloc.metadata.jit.type_info import TypeInfo


def test_type_info():
    @dataclass
    class Base:
        x: int
        y: str

        def f(self) -> None:
            ...

        def h(self) -> None:
            ...

    @dataclass
    class Derived(Base):
        z: int

        def f(self) -> None:
            ...

        def g(self) -> None:
            ...

    derived_type_info = TypeInfo.from_py_type(Derived)
    assert derived_type_info.name == "Derived"
    assert derived_type_info.py_type == Derived
    assert len(derived_type_info.fields) == 3
    assert derived_type_info.fields[0].name == "x"
    assert derived_type_info.fields[2].name == "z"
    assert derived_type_info.fields[2].type.name == "int"
    assert len(derived_type_info.methods) == 3
    assert derived_type_info.methods[1].method == Base.h
    parent = derived_type_info.parent
    assert isinstance(parent, TypeInfo)
    assert parent.py_type == Base
    assert len(parent.fields) == 2
    assert len(parent.methods) == 2
