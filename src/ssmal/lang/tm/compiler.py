from collections import defaultdict
import io
from typing import Generator, Literal

from ssmal.lang.tm.parser import parse_tm_transitions
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
        # fmt: off
        (self.tm_assembler_writer
            .label_state(self.cur_state)
            .indent()
                .save_B()
                .three_way_switch(self.cur_state)
                .newline())
        for case in self.cases:
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
        return (
            self.tm_assembler_writer
            .dedent()
            .align()
            .comment(f"end of {self.cur_state}")
            .newline(2)
        )
        # fmt: on


class TmCompiler:
    tm_assembler_writer: TmAssemblerWriter

    def __init__(self) -> None:
        self.tm_assembler_writer = TmAssemblerWriter()

    def _write_halt(self, label: Literal["FAIL", "SUCCESS"]) -> TmAssemblerWriter:
        # fmt: off
        return (
            self.tm_assembler_writer.write_line(".align")
            .label_state(label)
            .indent()
                .write_line(f"ldai ${label}_message")
                .write_line("ldai 0 sys halt")
                .write_line(".align")
                .label(f"{label}_message")
                .write_line(f' "{label}"')
            .dedent()
        )
        # fmt: on

    def _write_builtins(self):
        self._write_halt("FAIL").newline(2)
        self._write_halt("SUCCESS")

    def compile(self, transitions: list[TmTransition]):
        transitions_by_cur_state: defaultdict[str, list[TmTransition]] = defaultdict(list)
        for transition in transitions:
            transitions_by_cur_state[transition.cur_state].append(transition)

        for cur_state, transition_group in transitions_by_cur_state.items():
            transition_compiler = TransitionCompiler(self.tm_assembler_writer, cur_state, transition_group)
            transition_compiler.compile_transition()

        self._write_builtins()

    def compile_file(self, filename: str):
        with open(filename) as f:
            text = f.read()
        transitions = list(parse_tm_transitions(text))
        self.compile(transitions)

    @property
    def assembly(self) -> str:
        return self.tm_assembler_writer.text
