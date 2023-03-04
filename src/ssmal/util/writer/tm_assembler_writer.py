from __future__ import annotations

from typing import Callable, Literal, ParamSpec, TypeVar
from ssmal.util.writer.assembler_writer import AssemblerWriter
from functools import wraps

Self = TypeVar("Self", bound="AssemblerWriter")
T = TypeVar("T", bound="TmAssemblerWriter")
P = ParamSpec("P")


class TmAssemblerWriter(AssemblerWriter):
    def label_state(self: Self, state: str) -> Self:
        return self.label(state).newline()

    def label_case(self: Self, state: str, case: Literal["0", "1", "2"]) -> Self:
        return self.label(f"{state}_case_{case}").newline()

    def save_B(self: Self) -> Self:
        return self.write(f"swpab psha swpab").comment("save B to stack")

    def restore_B(self: Self) -> Self:
        return self.write(f"popa swpab").comment("restore B from stack")

    def three_way_switch(self: Self, state: str) -> Self:
        # fmt: off
        return (
            self.write(f"ldab addi -1").comment("B points to head")
            .indent()
                .write(f"brni ${state}_case_0").comment("head is 0")
                .write(f"brzi ${state}_case_1").comment("head is 1")
                .write(f"bri ${state}_case_2").comment("head is 2")
                .align()
            .dedent()
        )

    def write_head(self: Self, value: Literal["0", "1", "2"]) -> Self:
        return self.write(f"ldai {value} stab").comment(f"write {value} to head")

    def move_head(self: Self, direction: Literal["L", "R", "STAY"]) -> Self:
        i = {"L": -1, "R": 1, "STAY": 0}[direction]
        return self.write(f"swpab addi {i} swpab").comment(f"move {direction}")

    def goto(self: Self, next_state: str) -> Self:
        return self.write(f"""bri ${next_state}""").comment(f"goto {next_state}")
