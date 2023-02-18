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
        (sys_io.PREG, b'', str(Registers(A=sys_io.PREG, SP=9))),
    ],
)
def test_PSH_POP_A(A: int, _memory: bytes, expected_out: str):
    m = Memory()
    r = Registers(A=A, SP=9)
    m.store(0, 0x80)
    m.store_bytes(1, _memory)
    cout = io.StringIO()
    cin = io.StringIO()
    sys_io.SYS(r, m, cout=cout, cin=cin)
    assert cout.getvalue()[:len(expected_out)] == expected_out