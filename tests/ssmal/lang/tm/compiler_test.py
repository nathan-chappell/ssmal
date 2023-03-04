from pprint import pprint
import logging
from typing import Literal

import pytest

from ssmal.assemblers.tokenizer import tokenize
from ssmal.assemblers.assembler import Assembler
from ssmal.components.memory import MonitoredWrite
from ssmal.lang.tm.loader import TmLoader
from ssmal.lang.tm.parser import parse_tm_transitions
from ssmal.lang.tm.compiler import TmCompiler, TransitionCompiler
from ssmal.processors.processor import Processor
from ssmal.util.ascii_safe_encode import ascii_safe_encode
from ssmal.util.hexdump_bytes import hexdump_bytes
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
ones 2 twos 0 R

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
    text_bytes = assembler.buffer.getvalue()

    p = Processor()
    p.log.setLevel(logging.DEBUG)
    p.log.debug(f"Object length length: {len(text_bytes)}")

    data_bytes = b"".join(x.to_bytes(4, "little") for x in input)

    tm_loader = TmLoader(text_bytes=text_bytes, data_bytes=data_bytes)
    # tm_loader.log.setLevel(logging.DEBUG)
    tm_loader.load_program(p)

    # p.memory.dump()

    class HeardResult(Exception):
        zstr: str

        def __init__(self, zstr: str, *args: object) -> None:
            super().__init__(*args)
            self.zstr = zstr

    def _listen_result(*args, **kwargs) -> None:
        _bytes = p.memory.load_bytes(p.memory.load(p.registers.SP - 4), 100)
        _bytes = _bytes[:_bytes.index(b'\x00')]
        _result = ascii_safe_encode(_bytes)
        if "SUCCESS" in _result or "FAIL" in _result:
            raise HeardResult(_result)
        else:
            print(_result)

    p.sys_vector[0] = _listen_result

    try:
        for _ in range(100):
            p.advance()
        else:
            assert False
    except HeardResult as result:
        assert result.zstr == expected
