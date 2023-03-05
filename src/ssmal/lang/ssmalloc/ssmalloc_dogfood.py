from __future__ import annotations
from dataclasses import dataclass
from typing import cast

ARENA_SIZE: int = 0x400
arena: bytes = bytes(ARENA_SIZE)


@dataclass
class MallocNode:
    start: int
    end: int
    next: MallocNode | int
    free: int

    SIZE = 0x10


MALLOC_ARENA_SIZE = 0x400
malloc_list_arena: bytes = bytes(MALLOC_ARENA_SIZE)


def malloc(size: int) -> int:
    node: MallocNode = cast(MallocNode, malloc_list_arena)
    while True:
        if node.free == 0:
            if node.next == 0:
                exit(-1)
            node = cast(MallocNode, node.next)
        if node.end - node.start - MallocNode.SIZE <= size:
            next_node: MallocNode = cast(MallocNode, node.start + size)
            next_node.start = node.start + size + MallocNode.SIZE
            next_node.end = node.end
            next_node.free = 1
            node.end = node.start + size
            node.free = 0
            return node.start
