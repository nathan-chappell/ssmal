import pytest

from ssmal.lang.ssmalloc.arena import Arena
from ssmal.lang.ssmalloc.ssmal_type import SsmalType
from ssmal.lang.ssmalloc.ssmal_rtti import SsmalRttiManager


def test_store_type():
    view = memoryview(bytearray(0x400))
    arena = Arena(view)
    rtti = SsmalRttiManager(arena)
    small_type = SsmalType(None, 2, "Point", ("x", "y"))
    rtti.store_type(small_type)
    assert rtti.load_type(small_type.name) == small_type


def test_store_type_point_with_base():
    view = memoryview(bytearray(0x400))
    arena = Arena(view)
    rtti = SsmalRttiManager(arena)

    from dataclasses import dataclass

    @dataclass
    class Point2D:
        x: int
        y: int

    @dataclass
    class Point3D(Point2D):
        z: int

    point_3d_type = SsmalType.from_type(Point3D)
    assert point_3d_type.base_type is not None, "base type not created"
    rtti.store_type(point_3d_type.base_type)
    rtti.store_type(point_3d_type)
    assert rtti.load_type(point_3d_type.name) == point_3d_type
