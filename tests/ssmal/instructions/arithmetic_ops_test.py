import pytest

import ssmal.instructions.arithmetic_ops as op

from ssmal.components.memory import Memory
from ssmal.components.registers import Registers


@pytest.mark.parametrize("op_name,A,B,expected", [("ADDB", 3, 4, 7), ("SUBB", 3, 4, -1), ("MULB", 3, 4, 12), ("DIVB", 3, 4, 0)])
def test_opsB(op_name: str, A: int, B: int, expected: int):
    r = Registers(A=A, B=B)
    m = Memory(0)
    op.__dict__[op_name](r, m)
    assert r.A == expected


@pytest.mark.parametrize("op_name,A,i,expected", [("ADDi", 3, 4, 7), ("SUBi", 3, 4, -1), ("MULi", 3, 4, 12), ("DIVi", 3, 4, 0)])
def test_opsi(op_name: str, A: int, i: int, expected: int):
    IP = 1
    r = Registers(A=A, IP=IP)
    m = Memory(6)
    m.store(IP + 1, i)
    op.__dict__[op_name](r, m)
    assert r.A == expected


@pytest.mark.parametrize(
    "op_name,A,B,v,expected", [("ADD_", 3, 0, 4, 7), ("SUB_", 3, 1, 4, -1), ("MUL_", 3, 2, 4, 12), ("DIV_", 3, 2, 4, 0)]
)
def test_opsb(op_name: str, A: int, B: int, v: int, expected: int):
    r = Registers(A=A, B=B)
    m = Memory(6)
    m.store(r.B, v)
    op.__dict__[op_name](r, m)
    assert r.A == expected
