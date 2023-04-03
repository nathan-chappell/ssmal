from __future__ import annotations

from dataclasses import dataclass

import math


@dataclass
class Interval:
    """Half open on the right."""

    l: int
    r: int

    def __repr__(self) -> str:
        width = int(math.ceil(math.log(max(self.l, self.r), 256)))
        _l = self.l.to_bytes(width, 'big', signed=False).hex()
        _r = self.r.to_bytes(width, 'big', signed=False).hex()
        return f"Interval(0x{_l}, 0x{_r})"

    def __le__(self, other: Interval) -> bool:
        """Is subset of"""
        return other.l <= self.l and self.r <= other.r

    def __ge__(self, other: Interval) -> bool:
        """Is superset of"""
        return other <= self

    def __and__(self, other: Interval) -> Interval:
        """Intersection"""
        return Interval(max(self.l, other.l), min(self.r, other.r))

    def __or__(self, other: Interval) -> Interval:
        """Union"""
        return Interval(min(self.l, other.l), max(self.r, other.r))

    def __bool__(self) -> bool:
        """Not Empty"""
        return self.l < self.r

    def __contains__(self, x: int) -> bool:
        return self.l <= x and x < self.r
