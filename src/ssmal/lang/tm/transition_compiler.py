from typing import Literal
from ssmal.lang.tm.transtion import TmTransition
from ssmal.util.writer.tm_assembler_writer import TmAssemblerWriter


class TransitionCompiler:
    tm_assembler_writer: TmAssemblerWriter
    cur_state: str
    cases: list[TmTransition]

    def __init__(self, tm_assembler_writer: TmAssemblerWriter, cur_state: str, cases: list[TmTransition]) -> None:
        assert len(cases) > 0, "At least one case must be defined for a transition to compile"
        assert all([case.cur_state == cur_state for case in cases])
        self.tm_assembler_writer = tm_assembler_writer
        self.cur_state = cur_state
        self.cases = cases

    def compile_transition(self) -> TmAssemblerWriter:
        missing_cases: set[Literal["0", "1", "2"]] = {"0", "1", "2"}
        # fmt: off
        (self.tm_assembler_writer
            .label_state(self.cur_state)
            .indent()
                .save_B()
                .three_way_switch(self.cur_state)
                .newline())
        for case in self.cases:
            missing_cases.remove(case.cur_symbol)
            # fmt: off
            (self.tm_assembler_writer
            .label_case(self.cur_state, case.cur_symbol)
            .indent()
                .restore_B()
                .write_head(case.next_symbol)
                .move_head(case.move_head)
                .goto(case.next_state)
                .align()
            .dedent())
        for case in missing_cases:
            self.tm_assembler_writer.label_case(self.cur_state, case)
        return (
            self.tm_assembler_writer
            .dedent()
            .align()
            .comment(f"end of {self.cur_state}")
            .newline(2)
        )
        # fmt: on