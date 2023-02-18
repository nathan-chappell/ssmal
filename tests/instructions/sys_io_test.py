from tests import path_fix

path_fix()

import io

import pytest

import instructions.sys_io as sys_io

from components.memory import Memory
from components.registers import Registers


@pytest.mark.parametrize(
    "A,_memory,expected_out,",
    [
        (sys_io.PREG, b'\x80', str(Registers(A=sys_io.PREG, SP=9))),
        (sys_io.PTOPi, b'\x80\x00\x00\x00\x00\x01\x01\x00\x00', "257"),
        (sys_io.PTOPx, b'\x80\x00\x00\x00\x00\x01\x01\x00\x00', "0x00000101"),
        (sys_io.PTOPz, b'\x80\x41\x42\x43\x00\x01\x00\x00\x00', "ABC"),
    ],
)
def test_sys_io(A: int, _memory: bytes, expected_out: str):
    m = Memory()
    r = Registers(A=A, SP=9)
    m.store_bytes(0, _memory)
    cout = io.StringIO()
    cin = io.StringIO()
    sys_io.SYS(r, m, cout=cout, cin=cin)
    assert cout.getvalue()[:len(expected_out)] == expected_out
    assert cout.getvalue() == expected_out