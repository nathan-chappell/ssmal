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
from ssmal.lang.ssmalloc.metadata.jit.jit_parser import JitParser
from ssmal.lang.ssmalloc.metadata.jit.strongly_typed_strings import Identifier, TypeName
from ssmal.processors.processor import Processor

from ssmal.lang.ssmalloc.metadata.jit.type_info import TypeInfo, int_type, str_type
from ssmal.lang.ssmalloc.metadata.jit.codegen.scope import Scope
from ssmal.lang.ssmalloc.metadata.jit.codegen.method_compiler import MethodCompiler
from ssmal.util.writer.line_writer import LineWriter


@dataclass
class Base1:
    x: int
    s: str

    def f(self, y: int) -> int:
        z: int = self.x * y
        return z


@pytest.fixture
def Base1_method_compiler():
    Base_type_info = TypeInfo.from_py_type(Base1)
    assembler_writer = LineWriter()

    method_compiler = MethodCompiler(assembler_writer, JitParser.builtin_type_info(), Base_type_info)
    yield method_compiler


def prepare_and_run_Base1_f_to_halt(Base1_method_compiler: MethodCompiler, x: int, y: int) -> int:
    method = Base1_method_compiler.self_type.methods[0]
    Base1_method_compiler.reset_variable_types(method)
    assert len(Base1_method_compiler.variable_types) == 2
    assert Base1_method_compiler.variable_types[Identifier("self")] == Base1_method_compiler.self_type
    assert Base1_method_compiler.variable_types[Identifier("y")] == int_type
    Base1_method_compiler.compile_method(method)
    assembly_code = Base1_method_compiler.line_writer.text

    assembly_code = f"""
    halt nop nop nop "abc" .align
    {assembly_code}
    .goto 0x100
    -1 {x} 4  ; 0x100 self
    .goto 0x11c
    0       ; 0x11c return address
            ; stack start
    0x100   ; 0x120 self
    {y}     ; 0x124 y
    0xbeef  ; 0x128 z
    """
    print(assembly_code)
    assembly_code_lines = assembly_code.split("\n")

    assembler = Assembler(list(tokenize(assembly_code)))
    assembler.assemble()
    code_text = assembler.buffer.getvalue()

    processor = Processor()
    processor.memory.store_bytes(0, code_text)
    processor.registers.IP = 0x20
    processor.registers.SP = 0x128

    # processor.memory.monitor(0, 0x140)
    processor.memory.dump()
    _source_line = -1
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


def test_infer_type(Base1_method_compiler: MethodCompiler):
    f_ast = ast.parse(textwrap.dedent(inspect.getsource(Base1_method_compiler.self_type.methods[0].method))).body[0]
    assert isinstance(f_ast, ast.FunctionDef)
    body_0 = f_ast.body[0]
    assert isinstance(body_0, ast.AnnAssign)
    assert isinstance(body_0.value, ast.BinOp)
    Base1_method_compiler.reset_variable_types(Base1_method_compiler.self_type.methods[0])
    Base1_method_compiler.variable_types[Identifier("y")] = int_type
    assert Base1_method_compiler.infer_type(body_0.value).name == "int"


@pytest.mark.parametrize("x,y", [(-2, 3), (4, 0)])
def test_assemble_basic_method(x: int, y: int, Base1_method_compiler: MethodCompiler):
    assert prepare_and_run_Base1_f_to_halt(Base1_method_compiler, x, y) == Base1(x=x, s="").f(y)
