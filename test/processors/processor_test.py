import sys

sys.path.append("C:\\Users\\natha\\programming\\py\\ssmal\\src")

import pytest

from processors.processor import Processor


@pytest.mark.parametrize(
    "op,op_name,A,B,expected",
    [
        (b"\x10", "ADDB", 3, 4, 7),
        (b"\x11", "SUBB", 3, 4, -1),
        (b"\x12", "MULB", 3, 4, 12),
        (b"\x13", "DIVB", 3, 4, 0),
    ],
)
def test_opsB(op: bytes, op_name: str, A: int, B: int, expected: int):
    p = Processor()
    p.memory.store_bytes(0, op)
    p.registers.A = A
    p.registers.B = B
    p.advance()
    assert p.registers.A == expected


@pytest.mark.parametrize(
    "op,op_name,A,i,expected",
    [
        (b"\x14", "ADDi", 3, 4, 7),
        (b"\x15", "SUBi", 3, 4, -1),
        (b"\x16", "MULi", 3, 4, 12),
        (b"\x17", "DIVi", 3, 4, 0),
    ],
)
def test_opsi(op: bytes, op_name: str, A: int, i: int, expected: int):
    p = Processor()
    IP = 1
    p.memory.store_bytes(IP, op)
    p.registers.A = A
    p.registers.IP = IP
    p.memory.store(IP + 1, i)
    p.advance()
    assert p.registers.A == expected


@pytest.mark.parametrize(
    "op,op_name,A,B,v,expected",
    [
        (b"\x18", "ADDb", 3, 1, 4, 7),
        (b"\x19", "SUBb", 3, 1, 4, -1),
        (b"\x1a", "MULb", 3, 2, 4, 12),
        (b"\x1b", "DIVb", 3, 2, 4, 0),
    ],
)
def test_opsb(op: bytes, op_name: str, A: int, B: int, v: int, expected: int):
    p = Processor()
    p.memory.store_bytes(0, op)
    p.registers.A = A
    p.registers.B = B
    p.memory.store(B, v)
    p.advance()
    assert p.registers.A == expected