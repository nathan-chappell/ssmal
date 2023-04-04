from dataclasses import dataclass


@dataclass
class Program:
    @staticmethod
    def main() -> None:
        print("hello world")
