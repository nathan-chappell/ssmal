from tests import path_fix
path_fix()

import pytest

import instructions.stack_ops as op

from components.memory import Memory
from components.registers import Registers


@pytest.mark.parametrize("address,value", [(2, 1), (3, -1)])
def test_PSH_POP_A(address: int, value: int):
    m = Memory()
    r = Registers(A=value, SP=address)
    op.__dict__["PSHA"](r, m)
    assert r.SP == address + 4
    r.A = 0
    assert r.A != value
    op.__dict__["POPA"](r, m)
    assert r.A == value
    assert r.SP == address


@pytest.mark.parametrize("start,address", [(0,8), (2,8)])
def test_CALi(start: int, address: int):
    m = Memory()
    r = Registers(IP=start, SP=16)
    m.store(start + 1, address)
    op.__dict__["CALi"](r, m)
    assert r.SP == 20
    assert r.IP == address
    op.__dict__["RETN"](r, m)
    assert r.SP == 16
    assert r.IP == start + 5

@pytest.mark.parametrize("start,A", [(0,8), (2,8)])
def test_CALA(start: int, A: int):
    m = Memory()
    r = Registers(IP=start, SP=16, A=A)
    op.__dict__["CALA"](r, m)
    assert r.SP == 20
    assert r.IP == A
    op.__dict__["RETN"](r, m)
    assert r.SP == 16
    assert r.IP == start + 1

@pytest.mark.parametrize("start,A,address", [(0,8,12), (2,8,12)])
def test_CAL_(start: int, A: int, address: int):
    m = Memory()
    r = Registers(IP=start, SP=16, A=A)
    m.store(A, address)
    op.__dict__["CAL_"](r, m)
    assert r.SP == 20
    assert r.IP == address
    op.__dict__["RETN"](r, m)
    assert r.SP == 16
    assert r.IP == start + 1