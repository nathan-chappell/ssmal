import pytest

from ssmal.lang.ssmalloc.ssmal_type import SsmalType


def test_small_type_point():
    from dataclasses import dataclass

    @dataclass
    class Point:
        x: int
        y: int

    expected = SsmalType(None, 2, "Point", ("x", "y"))
    assert SsmalType.from_type(Point) == expected


def test_small_type_point_with_base():
    from dataclasses import dataclass

    @dataclass
    class Point2D:
        x: int
        y: int

    @dataclass
    class Point3D(Point2D):
        z: int

    expected = SsmalType(SsmalType.from_type(Point2D), 3, "Point3D", ("x", "y", "z"))
    assert SsmalType.from_type(Point3D) == expected
