import io

import pytest

import ssmal.instructions.sys as sys

from ssmal.components.memory import Memory
from ssmal.components.registers import Registers


@pytest.mark.parametrize(
    "A,_memory,expected_out,",
    [
        (sys.PREG, b"\x80", str(Registers(A=sys.PREG, SP=9))),
        (sys.PTOPi, b"\x80\x00\x00\x00\x00\x01\x01\x00\x00", "257"),
        (sys.PTOPx, b"\x80\x00\x00\x00\x00\x01\x01\x00\x00", "0x00000101"),
        (sys.PTOPz, b"\x80\x41\x42\x43\x00\x01\x00\x00\x00", "ABC"),
    ],
)
def test_sys(A: int, _memory: bytes, expected_out: str):
    m = Memory()
    r = Registers(A=A, SP=9)
    m.store_bytes(0, _memory)
    cout = io.StringIO()
    cin = io.StringIO()
    sys.SYS(r, m, cout=cout, cin=cin)
    assert cout.getvalue()[: len(expected_out)] == expected_out
    assert cout.getvalue() == expected_out
