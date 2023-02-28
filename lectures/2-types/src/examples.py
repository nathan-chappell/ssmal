"""simple_types.py

"""
from __future__ import annotations

import typing as T

"""
# Generics, Covariance, Contravariance, and a recursive type!
"""

TLeaf = T.TypeVar("TLeaf")
# TLeaf = T.TypeVar('TLeaf', covariant=True)
# TLeaf = T.TypeVar('TLeaf', contravariant=True)

NatList = None | T.Tuple[int, "NatList"]

x: NatList = (1, (2, None))


class Tree(T.Generic[TLeaf]):
    left: T.Optional["Tree[TLeaf]"] = None
    right: T.Optional["Tree[TLeaf]"] = None
    value: T.Optional[TLeaf] = None


class Base:
    ...


class Derived(Base):
    ...


tbase: Tree[Base] = Tree()
tderived: Tree[Derived] = Tree()

# tbase = tderived
# tderived = tbase

# Most straight-forward OOP recursive type...


class ListNode:
    value: int
    next: None | ListNode

    def __init__(self, value: int, next: None | ListNode = None):
        self.value = value
        self.next = next

    @staticmethod
    def demo_create() -> "ListNode":
        return ListNode(1, ListNode(2, None))


# Notice difference with:

TListNode = None | tuple[int, "TListNode"]


def demo_t_list_node():
    t_list_node: TListNode
    t_list_node = (1, (2, None))

    # what about this?
    t_list_node = None
    list_node: ListNode = None


#############
#############
#############
#############
#############
#############
# Exercise: make it generic...
#############
#############
#############
#############
#############
#############

NodeType = T.TypeVar("NodeType")


class GenericListNode(T.Generic[NodeType]):
    value: NodeType
    next: None | GenericListNode[NodeType]

    def __init__(self, value: NodeType, next: None | GenericListNode[NodeType] = None):
        self.value = value
        self.next = next

    @staticmethod
    def demo_create(t: NodeType) -> GenericListNode[NodeType]:
        # mypy catches this
        result = GenericListNode("foo", GenericListNode(2, None))
        return result


TGenericNodeList = None | tuple[NodeType, "TGenericNodeList[NodeType]"]


def demo_t_generic_list_node():
    t_list_node: TListNode
    # t_list_node = (1,('foo',None))

    # what about this?
    t_list_node = None
    # list_node: GenericListNode[int] = None
    r = GenericListNode[int].demo_create("foo")
    r = GenericListNode[object].demo_create("foo")


l: list[int] = list[int](["foo", "bar"])
