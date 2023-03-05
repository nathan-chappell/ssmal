# from typing import Any
# from ssmal.lang.ssmalloc.arena import Arena, default_arena


# class ArenaProxyMeta(type):
#     arena: Arena = default_arena

#     def __new__(cls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> type:
#         def __new__(_cls, *args):
#             # address = cls.arena.malloc(SsmalType.from_type(_cls).size)
#             address = cls.arena.malloc()
#             if address == -1:
#                 raise MemoryError("out of arena memory")
#             return ArenaProxy(_cls, address, *args)

#         namespace["__new__"] = __new__
#         return type(name, bases, namespace)


# @dataclass
# class Point(metaclass=ArenaProxyMeta):
#     x: int
#     y: int


# print(arena[:0x10])
# p = Point(0, 0)
# p.x = 0x12
# p.y = 0x1235
# print(arena[:0x10])
