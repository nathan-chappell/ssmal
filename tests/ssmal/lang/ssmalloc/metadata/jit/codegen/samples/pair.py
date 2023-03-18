from dataclasses import dataclass


@dataclass
class Pair:
    x: int = 0
    y: int = 0

    def sum(self) -> int:
        return self.x + self.y


@dataclass
class Program:
    @staticmethod
    def main() -> None:
        p: Pair = Pair()
        p.x = 1
        p.y = 2
        print(p.sum())
