from __future__ import annotations

from dataclasses import dataclass

@dataclass
class Summable:
    
    def sum(self) -> int:
        return 0
    
    def add(self, other: Summable) -> int:
        return self.sum() + other.sum()

@dataclass
class Pair(Summable):
    x: int = 0
    y: int = 0

    def sum(self) -> int:
        return self.x + self.y


@dataclass
class Triple(Summable):
    x: int = 0
    y: int = 0
    z: int = 0

    def sum(self) -> int:
        return self.x + self.y + self.z


@dataclass
class Program:
    @staticmethod
    def main() -> None:
        t: Triple = Triple()
        t.x = 3
        t.y = 4
        t.z = 5
        p: Pair = Pair()
        p.x = 1
        p.y = 2
        p_sum: int = p.sum()
        t_sum: int = t.sum()
        r_sum: int = p_sum + t_sum
        print(r_sum)
