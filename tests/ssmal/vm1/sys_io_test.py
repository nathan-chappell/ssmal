import io
import pytest
from ssmal.components.memory import Memory
from ssmal.components.registers import Registers
import ssmal.vm1.sys_io as sys_io


def test_print_top_z():
    registers = Registers(SP=4)
    memory = Memory()
    memory.store(0, 8)
    memory.store_bytes(8, b"foo\x00")
    cin = io.StringIO()
    cout = io.StringIO()
    max_zstrlen = 0x20
    sys_io.print_top_z(registers, memory, cin, cout, max_zstrlen)
    assert cout.getvalue() == "foo"


def test_print_top_i():
    registers = Registers(SP=4)
    memory = Memory()
    memory.store(0, 123)
    cin = io.StringIO()
    cout = io.StringIO()
    max_zstrlen = 0x20
    sys_io.print_top_i(registers, memory, cin, cout, max_zstrlen)
    assert cout.getvalue() == "123"


def test_print_top_x():
    registers = Registers(SP=4)
    memory = Memory()
    memory.store(0, 0x00FF00E3)
    cin = io.StringIO()
    cout = io.StringIO()
    max_zstrlen = 0x20
    sys_io.print_top_x(registers, memory, cin, cout, max_zstrlen)
    assert cout.getvalue() == "0x00ff00e3"


def test_print_registers():
    registers = Registers(SP=4, A=1, B=2)
    memory = Memory()
    cin = io.StringIO()
    cout = io.StringIO()
    max_zstrlen = 0x20
    sys_io.print_registers(registers, memory, cin, cout, max_zstrlen)
    assert cout.getvalue() == str(registers)
