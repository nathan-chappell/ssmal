from dataclasses import dataclass

import pytest
from ssmal.lang.ssmalloc.arena import Arena

from ssmal.lang.ssmalloc.ssmal_type import SsmalField, SsmalType, OverrideInfo
from ssmal.lang.ssmalloc.ssmal_type_info import SsmalTypeEmbedder

def test_small_type():
    @dataclass
    class Point2D:
        name: str
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

    expected_point_2d_fields = tuple(SsmalField(name, _type) for name, _type in [("name", "str"), ("x", "int"), ("y", "int")])
    expected_point_2d = SsmalType(None, ("l2", "area"), "Point2D", expected_point_2d_fields)
    expected_point_3d_fields = (*expected_point_2d_fields, *(SsmalField(name, _type) for name, _type in [("z", "int")]))
    expected_point_3d = SsmalType(expected_point_2d, ("l2", "volume"), "Point3D", expected_point_3d_fields)

    symbol_table = {
        'Point2D.l2': 0x100,
        'Point2D.area': 0x100,
        'Point3D.l2': 0x100,
        'Point3D.volume': 0x100,
    }

    arena = Arena(memoryview(bytearray(0x400)))

    ssmal_type_embedder = SsmalTypeEmbedder(arena, [expected_point_2d, expected_point_3d], symbol_table)
    ssmal_type_embedder.embed()
    print(arena.view.tobytes())
    assert ssmal_type_embedder.hydrate('Point2D') == expected_point_2d