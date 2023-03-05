from __future__ import annotations

from dataclasses import dataclass, fields

_type_cache: dict[str, SsmalType] = {}
# maps name to address in arena...

# For simplicity, for now, all fields will be of size 4.
# TODO: document the datamodel:
#   * there are ints
#   * there are bytearrays
#   * there are pointers
FIELD_SIZE = 4


@dataclass
class SsmalType:
    base_type: SsmalType | None
    field_count: int
    name: str
    field_names: tuple[str, ...] = ()

    _type_cache = _type_cache

    @property
    def size(self) -> int:
        return FIELD_SIZE * len(self.field_names)

    @classmethod
    def from_type(cls, type: type) -> SsmalType:
        type_name = type.__name__
        if type_name not in cls._type_cache:
            if type_name == "SsmalType":
                raise NotImplementedError()
                # cls._type_cache[type_name] = SsmalType("ssmal_type", -1, 4, ["name", "base_type", "field_count", "field_names"])
            elif type_name == "int":
                raise NotImplementedError()
                # cls._type_cache[type_name] = SsmalType("int", -1, 1, ["value"])
            bases = type.__bases__
            if len(bases) > 1:
                raise NotImplementedError("Multiple inheritance not supported")
            elif len(bases) == 1 and bases[0] is not object:
                base_type = cls.from_type(bases[0])
            else:
                base_type = None
            field_names = [f.name for f in fields(type)]
            cls._type_cache[type_name] = SsmalType(base_type, len(field_names), type_name, tuple(field_names))
        return cls._type_cache[type_name]
