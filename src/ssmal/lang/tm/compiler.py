from collections import defaultdict
import io
from typing import Generator, Literal

from ssmal.lang.tm.parser import parse_tm_transitions
from ssmal.lang.tm.transition_compiler import TransitionCompiler
from ssmal.lang.tm.transtion import TmTransition
from ssmal.util.writer.tm_assembler_writer import TmAssemblerWriter


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
                .write_line(f"ldai ${label}_message psha")
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
