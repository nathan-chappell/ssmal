import pytest

from ssmal.lang.ssmalloc.arena import Arena
from ssmal.lang.ssmalloc.ssmal_type import SsmalType
from ssmal.lang.ssmalloc.ssmal_rtti import SsmalRttiManager


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

    point_3d_type = rtti.from_type(Point3D)
    assert point_3d_type.base_type is not None, "base type not created"
    rtti.store_type(point_3d_type.base_type)
    rtti.store_type(point_3d_type)
    assert rtti.load_type(point_3d_type.name) == point_3d_type


def test_store_type_vtable():
    view = memoryview(bytearray(0x400))
    arena = Arena(view)
    rtti = SsmalRttiManager(arena)

    from dataclasses import dataclass

    @dataclass
    class Point2D:
        x: int
        y: int

        def l2(self) -> int:
            return self.x * self.x + self.y * self.y

        def area(self) -> int:
            return self.x * self.y

    @dataclass
    class Point3D(Point2D):
        z: int

        def l2(self) -> int:
            return self.x * self.x + self.y * self.y + self.z * self.z

        def volume(self) -> int:
            return self.x * self.y * self.z

    rtti.method_impl_map['Point2D.l2'] = 0x0a00
    rtti.method_impl_map['Point2D.area'] = 0x0a10
    rtti.method_impl_map['Point3D.l2'] = 0x0b00
    rtti.method_impl_map['Point3D.area'] = 0x0b00
    rtti.method_impl_map['Point3D.volume'] = 0x0b10

    point_3d_type = rtti.from_type(Point3D)
    assert point_3d_type.base_type is not None, "base type not created"
    rtti.store_type(point_3d_type.base_type)
    rtti.store_type(point_3d_type)
    assert rtti.load_type(point_3d_type.name) == point_3d_type
