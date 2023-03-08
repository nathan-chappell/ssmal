from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, NoReturn, cast, ClassVar, Generic, TypeVar, overload

MAX_STRING_SIZE = 0x400


class BuiltInType:
    ...


class Int(BuiltInType):
    def __init__(self, value: int):
        ...

    def __iadd__(self, rhs: Int) -> Int:
        ...

    def __le__(self, rhs: Int) -> bool:
        ...


class Byte(BuiltInType):
    def __init__(self, value: bytes):
        ...

    def __iadd__(self, rhs: Byte) -> Byte:
        ...

    def __le__(self, rhs: Byte) -> bool:
        ...


class Ptr(Int):
    def __iadd__(self, rhs: Int) -> Ptr:
        ...


class Null(Ptr):
    def __init__(self):
        ...

    def __is__(self, other: Ptr) -> bool:
        ...


ItemType = TypeVar("ItemType")


class ArrayBase(Generic[ItemType], BuiltInType):
    size: Int = Int(0)
    address: Ptr = Null()

    def __init__(self, size: Int) -> None:
        ...

    def __getitem__(self, index: Int) -> ItemType:
        ...


class ByteArray(ArrayBase[Byte]):
    ...


class IntArray(ArrayBase[Int]):
    ...


class String(BuiltInType):
    buffer: ByteArray = ByteArray(Int(MAX_STRING_SIZE))

    def __init__(self, zstr: str):
        ...

    @overload
    def __eq__(self, other: String) -> bool:
        ...

    @overload
    def __eq__(self, other: Any) -> NoReturn:
        ...

    def __eq__(self, other: object) -> bool | NoReturn:
        ...
