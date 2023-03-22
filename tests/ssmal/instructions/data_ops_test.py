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


_boring_stack_values = (-7, -1, 1, 8)
_boring_stack_size = len(_boring_stack_values)
_boring_stack_bytes = b"".join(i.to_bytes(4, "little", signed=True) for i in _boring_stack_values)


@pytest.mark.parametrize(
    "offset, value, next_value", list((i, _boring_stack_values[_boring_stack_size - 1 - i], i + 0x20) for i in range(_boring_stack_size))
)
def test_STA_LDA__(offset: int, value: int, next_value: int):
    ip_offset_bytes = b"\xcc" + b"\xcc".join(offset.to_bytes(4, "little", signed=True) for _ in range(_boring_stack_size))

    IP = 0x10

    r = Registers(SP=0x10, IP=IP)
    m = Memory()
    m.store_bytes(0, _boring_stack_bytes + ip_offset_bytes)
    op.__dict__["LDA_"](r, m)
    assert r.A == value
    r.A = next_value
    op.__dict__["STA_"](r, m)
    r.A = 0
    assert r.A != next_value
    op.__dict__["LDA_"](r, m)
    assert r.A == next_value


# @pytest.mark.parametrize("pointer,address,value", [(0, 6, 1), (2, 7, -1)])
# def test_STA_LDA__(pointer: int, address: int, value: int):
#     m = Memory(16)
#     m.store(pointer, address)
#     m.store(address, value)
#     r = Registers(B=pointer)
#     op.__dict__["LDA_"](r, m)
#     assert r.A == value
