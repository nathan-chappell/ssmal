from dataclasses import dataclass

import pytest

from ssmal.lang.ssmalloc.ssmal_type import SsmalField, SsmalType, OverrideInfo

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

    assert SsmalType.from_dataclass(Point2D) == expected_point_2d
    assert SsmalType.from_dataclass(Point3D) == expected_point_3d

    assert expected_point_2d.override_table == {
        'l2': OverrideInfo.DeclaresNew,
        'area': OverrideInfo.DeclaresNew,
    }

    assert expected_point_3d.override_table == {
        'l2': OverrideInfo.DoesOverride,
        'area': OverrideInfo.DoesNotOverride,
        'volume': OverrideInfo.DeclaresNew,
    }

    assert expected_point_2d.get_implementer('l2') == expected_point_2d
    assert expected_point_2d.get_implementer('area') == expected_point_2d
    assert expected_point_3d.get_implementer('l2') == expected_point_3d
    assert expected_point_3d.get_implementer('area') == expected_point_2d
    assert expected_point_3d.get_implementer('volume') == expected_point_3d

    with pytest.raises(KeyError) as e:
        assert expected_point_3d.get_implementer("foobar")
    assert 'not in override table' in str(e.getrepr())
    
    expected_point_3d.base_type = None
    with pytest.raises(KeyError) as e:
        assert expected_point_3d.get_implementer("area")
    assert 'not in override table' in str(e.getrepr())
    expected_point_3d.base_type = expected_point_2d
