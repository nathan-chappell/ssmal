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
        return a,b

    f_ast = ast.parse(textwrap.dedent(inspect.getsource(f))).body[0]
    assert isinstance(f_ast, ast.FunctionDef)
    scope = Scope(f_ast)
    assert scope.get_offset("x") == 0
    assert scope.get_offset("y") == 1
    assert scope.get_offset("z") == 2
    assert scope.get_offset("a") == 3
    assert scope.get_offset("b") == 4


@pytest.mark.parametrize("varname,value", [("x", 3), ("y", 4), ("z", 5), ("a", 6), ("b", 7)])
def test_scope_codegen(varname: str, value: int):
    def f(x: int, y: str, z: int):
        a: str = "foo"
        b: int = 0
        return a,b

    f_ast = ast.parse(textwrap.dedent(inspect.getsource(f))).body[0]
    assert isinstance(f_ast, ast.FunctionDef)
    scope = Scope(f_ast)

    x, y, z, a, b = 3, 4, 5, 6, 7

    stack = b"".join(v.to_bytes(4, "little", signed=True) for v in (x, y, z, a, b))
    processor = Processor()
    processor.memory.store_bytes(0, stack)
    processor.registers.SP = 5 * 4

    line_writer = LineWriter()
    scope.access_variable(line_writer, varname, "eval")

    text = line_writer.text
    print(text)
    assembler = Assembler(list(tokenize(text)))
    assembler.assemble()
    IP = 0x40
    processor.memory.store_bytes(IP, assembler.buffer.getvalue())
    processor.registers.IP = IP

    processor.memory.dump()
    for _ in range(20):
        processor.advance()
        print(processor.registers)

    assert processor.registers.A == value
