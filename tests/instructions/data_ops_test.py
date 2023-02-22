import pytest

import ssmal.instructions.data_ops as op

from ssmal.components.memory import Memory
from ssmal.components.registers import Registers


@pytest.mark.parametrize("address,value", [(2, 1), (3, -1)])
def test_STA_LDA_i(address: int, value: int):
    m = Memory(6)
    m.store(address, value)
    r = Registers(IP=address - 1)
    op.__dict__["LDAi"](r, m)
    assert r.A == value


@pytest.mark.parametrize("address,value", [(2, 1), (3, -1)])
def test_STA_LDA_b(address: int, value: int):
    m = Memory(6)
    m.store(address, value)
    r = Registers(B=address)
    op.__dict__["LDAb"](r, m)
    assert r.A == value


@pytest.mark.parametrize("pointer,address,value", [(0, 6, 1), (2, 7, -1)])
def test_STA_LDA__(pointer: int, address: int, value: int):
    m = Memory(16)
    m.store(pointer, address)
    m.store(address, value)
    r = Registers(B=pointer)
    op.__dict__["LDA_"](r, m)
    assert r.A == value
