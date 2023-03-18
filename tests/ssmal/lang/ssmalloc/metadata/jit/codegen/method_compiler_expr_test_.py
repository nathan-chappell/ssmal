import ast
from collections import OrderedDict
from dataclasses import dataclass
import inspect
import textwrap

import pytest

from ssmal.assemblers.tokenizer import tokenize
from ssmal.assemblers.assembler import Assembler
from ssmal.components.memory import MonitoredWrite
from ssmal.instructions.processor_signals import HaltSignal
from ssmal.lang.ssmalloc.metadata.jit.strongly_typed_strings import Identifier, TypeName
from ssmal.processors.processor import Processor

from ssmal.lang.ssmalloc.metadata.jit.type_info import TypeInfo, int_type, str_type
from ssmal.lang.ssmalloc.metadata.jit.codegen.method_compiler import MethodCompiler
from ssmal.util.writer.line_writer import LineWriter


@dataclass
class Base1:
    def p1(self, x: int, y: int) -> int:
        z: int = 0x12121212
        return x

    def add(self, x: int, y: int) -> int:
        z: int = x + y
        return z

    def sub(self, x: int, y: int) -> int:
        z: int = x - y
        return z

    def mul(self, x: int, y: int) -> int:
        z: int = x * y
        return z

    def div(self, x: int, y: int) -> int:
        z: int = x // y
        return z


@pytest.fixture
def Base1_method_compiler():
    Base_type_info = TypeInfo.from_py_type(Base1)
    assembler_writer = LineWriter()

    method_compiler = MethodCompiler(assembler_writer, TypeInfo.builtin_type_info(), Base_type_info)
    yield method_compiler


def prepare_and_run_to_halt(Base1_method_compiler: MethodCompiler, method_name: str, *args: int) -> int:
    method = Base1_method_compiler.self_type.get_method_info(method_name)
    assert method is not None
    Base1_method_compiler.reset_variable_types(method)
    assert Base1_method_compiler.variable_types[Identifier("self")] == Base1_method_compiler.self_type
    Base1_method_compiler.compile_method(method)

    assembly_code = Base1_method_compiler.line_writer.text

    args_assembly = "\n".join([f"    {arg:4};    0x{0x120 + 4*i:03x} (args[{i}])" for i, arg in enumerate(args)]) + "\n"
    ret_addr_addr = 0x11C
    stack_size = len(args) + 2  # args + self + z

    assembly_code = f"""
    halt nop nop nop "abc" .align
    {assembly_code}
    .goto 0x100
    -1;      0x100 self
    .goto 0x11c
    0       ; 0x{ret_addr_addr:3x} return address
            ; stack start
    0x100   ; 0x120 self
{args_assembly}
    0xdeadbeef ; locals
    """
    print(assembly_code)
    assembly_code_lines = assembly_code.split("\n")

    assembler = Assembler(list(tokenize(assembly_code)))
    assembler.assemble()
    code_text = assembler.buffer.getvalue()

    processor = Processor()
    processor.memory.store_bytes(0, code_text)
    processor.registers.IP = 0x20
    processor.registers.SP = ret_addr_addr + 4 * (stack_size + 1)

    processor.memory.monitor(0, 0x11C)
    # processor.memory.dump()
    _source_line = -1
    processor.memory.dump()
    with pytest.raises(HaltSignal):
        for _ in range(80):
            op = processor.opcode_map.get(processor.memory.load_bytes(processor.registers.IP, 1), None)
            dbg = assembler.source_map.get(processor.registers.IP, None)
            if op and dbg:
                op_name = op.__name__
                if dbg.line != _source_line:
                    print(f"{processor.registers}, {op_name=} # {assembly_code_lines[dbg.line]}")
                    _source_line = dbg.line
                else:
                    print(f"{processor.registers}, {op_name=}")
            else:
                print(f"{processor.registers}, (IP NOT AT OP) {dbg=}")
            try:
                processor.advance()
            except MonitoredWrite as m:
                print(m.args)
                m.finish_write()

    processor.memory.dump()
    return processor.registers.A


@pytest.mark.parametrize(
    "method_name,x,y",
    [
        # fmt: off
    ('p1', -2,  3),
    ('add', -2,  3),
    ('add',  2, -300),
    ('sub', -2, -10),
    ('sub',  0,  0),
    ('mul', -2,  3),
    ('mul', -2,  -100),
    ('div',  0,  3),
    ('div',  1,  2),
        # fmt: on
    ],
)
def test_assemble_basic_method(method_name: str, x: int, y: int, Base1_method_compiler: MethodCompiler):
    assert prepare_and_run_to_halt(Base1_method_compiler, method_name, x, y) == Base1.__dict__[method_name](None, x, y)
