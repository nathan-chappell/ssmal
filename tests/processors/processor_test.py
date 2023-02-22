from tests import path_fix

path_fix()

import io
import typing as T
from functools import partial

import pytest

from processors.processor import Processor
from components.registers import Registers
import instructions.sys_io as sys_io
import instructions.processor_ops as processor_ops


@pytest.mark.parametrize(
    "op,op_name,A,B,expected",
    [
        (b"\x10", "ADDB", 3, 4, 7),
        (b"\x11", "SUBB", 3, 4, -1),
        (b"\x12", "MULB", 3, 4, 12),
        (b"\x13", "DIVB", 3, 4, 0),
    ],
)
def test_arithmetic_opsB(op: bytes, op_name: str, A: int, B: int, expected: int):
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
def test_arithmetic_opsi(op: bytes, op_name: str, A: int, i: int, expected: int):
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
        (b"\x18", "ADD_", 3, 1, 4, 7),
        (b"\x19", "SUB_", 3, 1, 4, -1),
        (b"\x1a", "MUL_", 3, 2, 4, 12),
        (b"\x1b", "DIV_", 3, 2, 4, 0),
    ],
)
def test_arithmetic_ops_(op: bytes, op_name: str, A: int, B: int, v: int, expected: int):
    p = Processor()
    p.memory.store_bytes(0, op)
    p.registers.A = A
    p.registers.B = B
    p.memory.store(B, v)
    p.advance()
    assert p.registers.A == expected


R = Registers


@pytest.mark.parametrize(
    "name,b0,r0,b1,r1",
    [
        ("LDAi", b"\x20\x02\x00\x00\x00", R(), None, R(A=2, IP=5)),
        ("LDAb", b"\x21\x05\x01\x00\x00", R(B=1), None, R(A=261, B=1, IP=1)),
        ("LDA_", b"\x22\x05\x00\x00\x00\xff\xff\xff\xff", R(B=1), None, R(A=-1, B=1, IP=1)),
        ("STAi", b"\x23", R(A=7), b"\x07\x00\x00\x00\x00", R(A=7, IP=5)),
        ("STAb", b"\x24", R(A=256, B=2), b"\x24\x00\x00\x00\x01\x00", R(A=256, B=2, IP=1)),
        ("STA_", b"\x25\x05\x00\x00\x00", R(B=1, A=-1), b"\x25\x05\x00\x00\x00\xff\xff\xff\xff", R(A=-1, B=1, IP=1)),
        ("PSHA", b"\x30", R(SP=1, A=0x12), b"\x25\x12\x00\x00\x00", R(SP=5, A=0x12, IP=1)),
        ("POPA", b"\x31\x12\x00\x00\x00", R(SP=5), None, R(SP=1, A=0x12, IP=1)),
        ("CALi", b"\x32\x20\x00\x00\x00", R(SP=5), b"\x32\x05\x00\x00\x00\x01\x00\x00\x00", R(IP=0x20, SP=9)),
        ("CALA", b"\x33", R(SP=1, A=0x66), b"\x32\x01\x00\x00\x00", R(IP=0x66, SP=5, A=0x66)),
        ("CAL_", b"\x34\x12\x00\x00\x00", R(SP=6, A=1), b"\x34\x12\x00\x00\x00\x00\x01\x00\x00\x00", R(IP=0x12, SP=10, A=1)),
        ("RETN", b"\x35\x00\x00\x00", R(SP=4), None, R(IP=0x35, SP=0)),
    ],
)
def test_processor_generic(
    name: str,
    b0: bytes,
    r0: Registers,
    b1: T.Optional[bytes],
    r1: Registers,
):
    p = Processor()
    p.memory.store_bytes(0, b0)
    p.registers = r0
    p.advance()
    assert p.memory.load_bytes(0, len(b1 or b0)) == b1 or b0
    assert p.registers == r1


@pytest.mark.parametrize(
    "A,_memory,expected_out,",
    [
        (sys_io.PREG, b"\x80", str(Registers(A=sys_io.PREG, SP=9))),
        (sys_io.PTOPi, b"\x80\x00\x00\x00\x00\x01\x01\x00\x00", "257"),
        (sys_io.PTOPx, b"\x80\x00\x00\x00\x00\x01\x01\x00\x00", "0x00000101"),
        (sys_io.PTOPz, b"\x80\x41\x42\x43\x00\x01\x00\x00\x00", "ABC"),
    ],
)
def test_sys_call(A: int, _memory: bytes, expected_out: str):
    p = Processor()
    p.memory.store_bytes(0, _memory)
    p.registers = Registers(A=A, SP=9)
    p.sys_io.bind(cin=io.StringIO(), cout=io.StringIO())
    p.advance()
    assert p.sys_io.cout.getvalue()[: len(expected_out)] == expected_out  # type: ignore
    assert p.sys_io.cout.getvalue() == expected_out  # type: ignore


def test_HALT():
    p = Processor()
    p.memory.store(0, 0x02)
    with pytest.raises(processor_ops.HaltSignal):
        p.advance()
