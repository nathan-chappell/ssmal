import ast
import inspect
import textwrap

import pytest

from ssmal.assemblers.tokenizer import tokenize
from ssmal.assemblers.assembler import Assembler
from ssmal.lang.ssmalloc.metadata.jit.codegen.scope import Scope
from ssmal.processors.processor import Processor
from ssmal.util.writer.line_writer import LineWriter


def test_scope_get_offset():
    def f(x: int, y: str, z: int):
        a: str = "foo"
        b: int = 0
        return a, b

    f_ast = ast.parse(textwrap.dedent(inspect.getsource(f))).body[0]
    assert isinstance(f_ast, ast.FunctionDef)
    scope = Scope(f_ast)
    assert scope.get_offset_from_top("x") == 4
    assert scope.get_offset_from_top("y") == 3
    assert scope.get_offset_from_top("z") == 2
    assert scope.get_offset_from_top("a") == 1
    assert scope.get_offset_from_top("b") == 0


@pytest.mark.parametrize("varname,value", [("x", 3), ("y", 4), ("z", 5), ("a", 6), ("b", 7)])
def test_scope_codegen(varname: str, value: int):
    def f(x: int, y: str, z: int):
        a: str = "foo"
        b: int = 0
        return a, b

    f_ast = ast.parse(textwrap.dedent(inspect.getsource(f))).body[0]
    assert isinstance(f_ast, ast.FunctionDef)
    scope = Scope(f_ast)

    vals = x, y, z, a, b = 3, 4, 5, 6, 7

    stack = b"".join(v.to_bytes(4, "little", signed=True) for v in vals)
    processor = Processor()
    processor.memory.store_bytes(0, stack)
    processor.registers.SP = 4 * len(vals)

    line_writer = LineWriter()
    scope.access_variable(line_writer, varname, "access")

    text = line_writer.text
    print(text)
    assembler = Assembler(list(tokenize(text)))
    assembler.assemble()
    IP = 0x40
    processor.memory.store_bytes(IP, assembler.buffer.getvalue())
    processor.registers.IP = IP

    # processor.memory.dump()
    for _ in range(2):
        processor.advance()
        # print(processor.registers)
    # processor.memory.dump()

    assert processor.registers.A == value

def test_scope_codegen():
    def f(x: int, y: str, z: int):
        a: str = "foo"
        b: int = 0
        return a, b

    f_ast = ast.parse(textwrap.dedent(inspect.getsource(f))).body[0]
    assert isinstance(f_ast, ast.FunctionDef)
    scope = Scope(f_ast)

    # x is pointer to y
    vals = x, y, z, a, b = 0x04, 0xbeef, 5, 6, 7

    stack = b"".join(v.to_bytes(4, "little", signed=True) for v in vals)
    processor = Processor()
    processor.memory.store_bytes(0, stack)
    processor.registers.SP = 4 * len(vals)

    line_writer = LineWriter()
    scope.access_variable(line_writer, "x", "eval")

    text = line_writer.text
    print(text)
    assembler = Assembler(list(tokenize(text)))
    assembler.assemble()
    IP = 0x40
    processor.memory.store_bytes(IP, assembler.buffer.getvalue())
    processor.registers.IP = IP

    # processor.memory.dump()
    for _ in range(4):
        processor.advance()
        # print(processor.registers)
    # processor.memory.dump()

    assert processor.registers.A == y