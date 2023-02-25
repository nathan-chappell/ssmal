"""simple_types.py

"""
from __future__ import annotations

import typing as T

"""
# Generics, Covariance, Contravariance, and a recursive type!
"""

TLeaf = T.TypeVar('TLeaf')
# TLeaf = T.TypeVar('TLeaf', covariant=True)
# TLeaf = T.TypeVar('TLeaf', contravariant=True)

NatList = T.Union[None, T.Tuple[int, 'NatList']]

x: NatList = (1,(2,None))

class Tree(T.Generic[TLeaf]):
    left: T.Optional['Tree[TLeaf]'] = None
    right: T.Optional['Tree[TLeaf]'] = None
    value: T.Optional[TLeaf] = None

class Base: ...
class Derived(Base): ...

tbase: Tree[Base] = Tree()
tderived: Tree[Derived] = Tree()

# tbase = tderived
# tderived = tbase


class C:
    c: C