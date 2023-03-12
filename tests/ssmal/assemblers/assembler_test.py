import pytest
from ssmal.assemblers.errors import UnresolvedLabelError

from ssmal.assemblers.token import Token
from ssmal.assemblers.tokenizer import tokenize
from ssmal.assemblers.assembler import Assembler
from ssmal.processors.opcodes import opcode_map

T = Token


def test_opcode_map():
    _all_ops = "nop dbg halt addb subb mulb divb addi subi muli divi add_ sub_ mul_ div_ ldai ldab lda_ stai stab sta_ psha popa cali cala cal_ retn sys swpab swpai movsa bri bra brzi brni brzb brnb"
    expected = b"\x00\x01\x02\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x20\x21\x22\x23\x24\x25\x30\x31\x32\x33\x34\x35\x80\x40\x41\x42\x50\x51\x52\x53\x54\x55"
    tokens = list(tokenize(_all_ops))
    assembler = Assembler(tokens)
    assembler.assemble()
    assert assembler.buffer.getvalue()[0 : len(expected)] == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (""" 0x1234 """, b"\x34\x12"),
        (""" .def x 0x1234 x """, b"\x34\x12"),
        (""" "abc" '001133' """, b"\x61\x62\x63\x00\x00\x11\x33"),
        (""" 1234 .goto 8 .here""", b"\xd2\x04\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00"),
        (""" 1234 foo: bri $foo""", b"\xd2\x04\x00\x00\x50\x04\x00\x00\x00"),
        (""" 1234 foo: bri $bar nop nop bar: nop""", b"\xd2\x04\x00\x00\x50\x0b\x00\x00\x00" b"\x00\x00"),
        (""" '01' .align '02' """, b"\x01" + b"\x00" * 0x1F + b"\x02"),
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
def test_assembler_directives(input: str, expected: dict[str, str]):
    tokens = list(tokenize(input))
    assembler = Assembler(tokens)
    assembler.assemble()
    assert {k: getattr(assembler, k) for k in expected.keys()} == expected


@pytest.mark.parametrize("input,error", [(""" 1234 foo: bri $bar nop nop""", UnresolvedLabelError)])
def test_assembler_errors(input: str, error: type):
    tokens = list(tokenize(input))
    assembler = Assembler(tokens)
    with pytest.raises(error):
        assembler.assemble()
