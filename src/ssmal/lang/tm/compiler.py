from collections import defaultdict
from typing import Literal
import io

from ssmal.lang.tm.parser import parse_tm_transitions
from ssmal.lang.tm.transtion import TmTransition


class TransitionCompiler:
    assembly: io.StringIO
    cur_state: str
    cases: list[TmTransition]

    def __init__(self, assembly: io.StringIO, cur_state: str, cases: list[TmTransition]) -> None:
        assert len(cases) > 0, "At least one case must be defined for a transition to compile"
        assert all([case.cur_state == cur_state for case in cases])
        self.assembly = assembly
        self.cur_state = cur_state
        self.cases = cases

    def _label_state(self):
        self.assembly.write(
            f"""
{self.cur_state}:"""
        )

    def _label_case(self, case: Literal["0", "1", "2"]):
        self.assembly.write(
            f"""
    {self.cur_state}_case_{case}:"""
        )

    def _save_B(self):
        self.assembly.write(
            f"""
    ; save B
    swpab psha swpab"""
        )

    def _restore_B(self):
        self.assembly.write(
            f"""
        ; restore b
        popa swpab"""
        )

    def _switch(self):
        self.assembly.write(
            f"""
    ; B points to position on tape
    ldab addi -1
        ; if 0
        brni ${self.cur_state}_case_0
        ; if 1
        brzi ${self.cur_state}_case_1
        ; else
        bri ${self.cur_state}_case_2
        .align
"""
        )

    def _write(self, value: Literal["0", "1", "2"]):
        self.assembly.write(
            f"""
        ; write value
        ldai {value} stab"""
        )

    def _move(self, direction: Literal["L", "R", "STAY"]):
        # i = {"L": -4, "R": 4, "STAY": 0}[direction]
        i = {"L": -1, "R": 1, "STAY": 0}[direction]
        self.assembly.write(
            f"""
        ; move {direction}
        swpab addi {i} swpab"""
        )

    def _goto(self, next_state: str):
        self.assembly.write(
            f"""
        ; goto state
        bri ${next_state}"""
        )

    def compile_transition(self):
        self._label_state()
        self._save_B()
        self._switch()
        for case in self.cases:
            self._label_case(case.cur_symbol)
            self._restore_B()
            self._write(case.next_symbol)
            self._move(case.move_head)
            self._goto(case.next_state)
            self.assembly.write(" .align ")
            self.assembly.write("\n")


class TmCompiler:
    assembly: io.StringIO

    def __init__(self) -> None:
        self.assembly = io.StringIO()

    def _align(self):
        self.assembly.write(
            """
        .align"""
        )

    def _builtin_states(self):
        self.assembly.write(
            f"""
.align
FAIL:
    ldai $fail_message
    psha
    ldai 0
    sys
    halt
    .align
    fail_message: "FAIL"

.align
SUCCESS:
    ldai $success_message
    psha
    ldai 0
    sys
    halt
    .align
    success_message: "SUCCESS"
"""
        )

    def compile(self, transitions: list[TmTransition]) -> None:
        transitions_by_cur_state: defaultdict[str, list[TmTransition]] = defaultdict(list)
        for transition in transitions:
            transitions_by_cur_state[transition.cur_state].append(transition)

        for cur_state, transition_group in transitions_by_cur_state.items():
            transition_compiler = TransitionCompiler(self.assembly, cur_state, transition_group)
            transition_compiler.compile_transition()
            self._align()

        self._builtin_states()

    def compile_file(self, filename: str):
        with open(filename) as f:
            text = f.read()
        transitions = list(parse_tm_transitions(text))
        self.compile(transitions)
