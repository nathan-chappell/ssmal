from pprint import pprint
import logging
from typing import Literal

import pytest

from ssmal.assemblers.tokenizer import tokenize
from ssmal.assemblers.assembler import Assembler
from ssmal.components.memory import MonitoredWrite
from ssmal.lang.tm.parser import parse_tm_transitions
from ssmal.lang.tm.compiler import TmCompiler, TransitionCompiler
from ssmal.processors.processor import Processor
from ssmal.util.writer.tm_assembler_writer import TmAssemblerWriter


@pytest.mark.parametrize("input, expected", [([1, 2], "SUCCESS")])
def test_compiler(input: list[int], expected: str):
    tm_text = """
# ones_then_twos
# read 1+ 2+

first_one 0 FAIL 0 R
first_one 1 ones 0 R
first_one 2 FAIL 0 R

ones 0 FAIL 0 R
ones 1 ones 0 R
ones 2 first_two 0 R

first_two 0 FAIL 0 R
first_two 1 FAIL 0 R
first_two 2 twos 0 R

twos 0 SUCCESS 0 R
twos 1 FAIL 0 R
twos 2 twos 0 R

"""
    transitions = list(parse_tm_transitions(tm_text))
    compiler = TmCompiler()
    compiler.compile(transitions)
    print(compiler.assembly)
    assembler = Assembler(list(tokenize(compiler.assembly)))
    assembler.assemble()
    object_bytes = assembler.buffer.getvalue()
    p = Processor()
    p.log.setLevel(logging.DEBUG)
    p.log.debug(f"Object length length: {len(object_bytes)}")
    p.memory.store_bytes(0, object_bytes)
    p.memory.dump()
    p.registers.SP = len(object_bytes) + 4
    end_of_stack = p.registers.SP + 0x20
    p.registers.B = end_of_stack

    for i, val in enumerate(input):
        INT_SIZE = 4
        p.memory.store(end_of_stack + i * INT_SIZE, val)

    _result: str | None = None

    class HeardResult(Exception):
        ...

    def _listen_result(*args, **kwargs) -> None:
        nonlocal _result
        _p = p
        # _result = str(p.memory.load_bytes(p.registers.A, len(expected)), "ascii")
        breakpoint()
        _result = str(p.memory.load_bytes(p.registers.SP, 4), "ascii")
        raise HeardResult()

    p.sys_vector[0] = _listen_result

    try:
        for _ in range(100):
            p.advance()
        else:
            assert False
    except HeardResult:
        assert _result == expected
