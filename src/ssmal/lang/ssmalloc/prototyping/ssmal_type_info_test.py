from dataclasses import dataclass

import pytest
from ssmal.lang.ssmalloc.metadata.util.arena import Arena

from ssmal.lang.ssmalloc.prototyping.ssmal_type import SsmalField, SsmalType, OverrideType
from ssmal.lang.ssmalloc.prototyping.ssmal_type_embedder import SsmalTypeEmbedder
from ssmal.util.hexdump_bytes import hexdump_bytes


def test_string_table():
    arena = Arena(memoryview(bytearray(0x400)))
    _strings: tuple[str, ...] = ("foo", "bar", "moo12")
    expected = b"foo\x00bar\x00moo12\x00\x00"

    ssmal_type_embedder = SsmalTypeEmbedder(arena, [], {})
    offsets, _bytes = ssmal_type_embedder.compile_string_table(_strings)
    assert _bytes == expected
    assert offsets == {"foo": 0, "bar": 4, "moo12": 8}


def test_hydrate():
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

    expected_point_2d_vtable: tuple[tuple[str, OverrideType], ...] = tuple(
        (("l2", OverrideType.DeclaresNew), ("area", OverrideType.DeclaresNew))
    )

    expected_point_3d_vtable: tuple[tuple[str, OverrideType], ...] = tuple(
        (("l2", OverrideType.DoesOverride), ("area", OverrideType.DoesNotOverride), ("volume", OverrideType.DeclaresNew))
    )

    expected_point_2d_fields = tuple(SsmalField(name, _type) for name, _type in [("name", "str"), ("x", "int"), ("y", "int")])
    expected_point_2d = SsmalType(None, expected_point_2d_vtable, "Point2D", expected_point_2d_fields)
    expected_point_3d_fields = (*expected_point_2d_fields, *(SsmalField(name, _type) for name, _type in [("z", "int")]))
    expected_point_3d = SsmalType(expected_point_2d, expected_point_3d_vtable, "Point3D", expected_point_3d_fields)

    symbol_table = {"Point2D.l2": 0x0AAAAAAA, "Point2D.area": 0x0BBBBBBB, "Point3D.l2": 0x0CCCCCCC, "Point3D.volume": 0x0DDDDDDD}

    arena = Arena(memoryview(bytearray(0x400)))

    ssmal_type_embedder = SsmalTypeEmbedder(arena, [expected_point_2d, expected_point_3d], symbol_table)
    ssmal_type_embedder.embed()

    print("\n".join(hexdump_bytes(ssmal_type_embedder.arena.view.tobytes())))
    str_address = ssmal_type_embedder.get_type_info_address_from_name("str")
    print(f"{str_address=:x}")
    # str_type = ssmal_type_embedder.hydrate('str')
    assert ssmal_type_embedder.get_type_name_from_type_info_address(str_address) == "str"
    assert ssmal_type_embedder.get_vtable_names_from_type_info_address(str_address) == ()
    assert ssmal_type_embedder.get_field_names_and_types_from_type_info_address(str_address) == ()

    point_2d_type_info_address = ssmal_type_embedder.get_type_info_address_from_name("Point2D")
    print(f"{point_2d_type_info_address=:x}")
    assert ssmal_type_embedder.get_type_name_from_type_info_address(point_2d_type_info_address) == "Point2D"
    assert ssmal_type_embedder.get_vtable_names_from_type_info_address(point_2d_type_info_address) == ("Point2D.l2", "Point2D.area")
    assert ssmal_type_embedder.get_field_names_and_types_from_type_info_address(point_2d_type_info_address) == (
        ("name", "str"),
        ("x", "int"),
        ("y", "int"),
    )

    point_2d_hydrated = ssmal_type_embedder.hydrate("Point2D")
    point_3d_hydrated = ssmal_type_embedder.hydrate("Point3D")
    assert point_2d_hydrated == expected_point_2d
    assert point_3d_hydrated == expected_point_3d
