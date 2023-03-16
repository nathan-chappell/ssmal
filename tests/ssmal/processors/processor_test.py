import io

from functools import partial
from typing import Optional

import pytest
from ssmal.instructions.processor_signals import ProcessorSignal, SysSignal, TrapSignal

from ssmal.processors.processor import Processor
from ssmal.components.registers import Registers

import ssmal.vm1.sys_io as sys_io
import ssmal.instructions.processor_ops as processor_ops


@pytest.mark.parametrize(
    "op,op_name,A,B,expected",
    [(b"\x10", "ADDB", 3, 4, 7), (b"\x11", "SUBB", 3, 4, -1), (b"\x12", "MULB", 3, 4, 12), (b"\x13", "DIVB", 3, 4, 0)],
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
    [(b"\x14", "ADDi", 3, 4, 7), (b"\x15", "SUBi", 3, 4, -1), (b"\x16", "MULi", 3, 4, 12), (b"\x17", "DIVi", 3, 4, 0)],
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
    [(b"\x18", "ADD_", 3, 1, 4, 7), (b"\x19", "SUB_", 3, 1, 4, -1), (b"\x1a", "MUL_", 3, 2, 4, 12), (b"\x1b", "DIV_", 3, 2, 4, 0)],
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
        ("LDAi", bytes.fromhex("2002000000"), R(), None, R(A=2, IP=5)),
        ("LDAb", bytes.fromhex("2105010000"), R(B=1), None, R(A=261, B=1, IP=1)),
        ("LDA_", bytes.fromhex("0102030422"), R(SP=4, IP=4), None, R(A=0x04030201, IP=9, SP=4)),
        ("STAi", bytes.fromhex("23"), R(A=7), bytes.fromhex("0700000000"), R(A=7, IP=5)),
        ("STAb", bytes.fromhex("24"), R(A=256, B=2), bytes.fromhex("240000000100"), R(A=256, B=2, IP=1)),
        ("STA_", bytes.fromhex("0000000025"), R(SP=4, IP=4, A=0x0102), bytes.fromhex("0201000022"), R(A=0x0102, IP=9, SP=4)),
        ("PSHA", bytes.fromhex("30"), R(SP=1, A=0x12), bytes.fromhex("2512000000"), R(SP=5, A=0x12, IP=1)),
        ("POPA", bytes.fromhex("3112000000"), R(SP=5), None, R(SP=1, A=0x12, IP=1)),
        ("CALi", bytes.fromhex("3220000000"), R(SP=5), bytes.fromhex("320500000001000000"), R(IP=0x20, SP=9)),
        ("CALA", bytes.fromhex("33"), R(SP=1, A=0x66), bytes.fromhex("3201000000"), R(IP=0x66, SP=5, A=0x66)),
        ("CAL_", bytes.fromhex("3412000000"), R(SP=6, A=1), bytes.fromhex("34120000000001000000"), R(IP=0x12, SP=10, A=1)),
        ("RETN", bytes.fromhex("35000000"), R(SP=4), None, R(IP=0x35, SP=0)),
    ],
)
def test_processor_generic(name: str, b0: bytes, r0: Registers, b1: Optional[bytes], r1: Registers):
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

    class TestSignal(Exception):
        ...

    def _raise_test(*args, **kwargs):
        raise TestSignal()

    p.sys_vector = {sys_io.PREG: _raise_test, sys_io.PTOPi: _raise_test, sys_io.PTOPx: _raise_test, sys_io.PTOPz: _raise_test}

    with pytest.raises(TestSignal):
        p.advance()


def test_HALT():
    p = Processor()
    p.memory.store(0, 0x02)
    with pytest.raises(processor_ops.HaltSignal):
        p.advance()


def test_Trap():
    p = Processor()
    p.memory.store(0, 0xFF)
    with pytest.raises(TrapSignal):
        p.advance()
