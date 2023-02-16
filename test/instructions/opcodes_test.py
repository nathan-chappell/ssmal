import sys
sys.path.append('D:\\programming\\py\\ssmal\\src')

import pytest

import instructions.opcodes as op

from components.memory import Memory
from components.registers import Registers


def test_ADDB():
    r = Registers()
    m = Memory(1)
    r.A = 3
    r.B = 4
    op.ADDB(r, m)
    assert r.A == 7
    m.buffer.seek(0)
    assert m.buffer.read() == b'\x00'