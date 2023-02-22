from typing import List, Dict

import pytest

from ssmal.assemblers.token import Token
from ssmal.assemblers.tokenizer import tokenize
from ssmal.assemblers.assembler import Assembler

T = Token


@pytest.mark.parametrize(
    "input,expected",
    [
        (
            """ 0x1234 """,
            b"\x34\x12",
        ),
        (
            """ .def x 0x1234 x """,
            b"\x34\x12",
        ),
        (
            """ addb subb mulb divb addi subi muli divi add_ sub_ mul_ div_ ldai ldab lda_ stai stab sta_ psha popa cali cala cal_ retn """,
            b"\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x20\x21\x22\x23\x24\x25\x30\x31\x32\x33\x34\x35",
        ),
        (
            """ "abc" '001133' """,
            b"\x61\x62\x63\x00\x00\x11\x33",
        ),
    ],
)
def test_assembler(input: str, expected: bytes):
    tokens = list(tokenize(input))
    assembler = Assembler(tokens)
    assembler.assemble()
    assert assembler.buffer.getvalue()[0 : len(expected)] == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (""" .encoding "latin1" """, {"encoding": "latin1"}),
        (""" .byteorder "big" """, {"byteorder": "big"}),
        (""" .goto 0x1234 """, {"current_position": 0x1234}),
    ],
)
def test_assembler_directives(input: str, expected: Dict[str, str]):
    tokens = list(tokenize(input))
    assembler = Assembler(tokens)
    assembler.assemble()
    assert {k: getattr(assembler, k) for k in expected.keys()} == expected
