import ast
from collections import OrderedDict
from dataclasses import dataclass
import inspect
import textwrap

import pytest

from ssmal.assemblers.tokenizer import tokenize
from ssmal.assemblers.assembler import Assembler
from ssmal.lang.ssmalloc.metadata.jit.strongly_typed_strings import Identifier, TypeName
from ssmal.processors.processor import Processor

from ssmal.lang.ssmalloc.metadata.jit.type_info import TypeInfo
from ssmal.lang.ssmalloc.metadata.jit.codegen.scope import Scope
from ssmal.lang.ssmalloc.metadata.jit.codegen.method_compiler import MethodCompiler


@pytest.mark.parametrize("varname,value", [("x", 3), ("y", 4), ("z", 5), ("a", 6), ("b", 7)])
def test_method_compiler_infer_type():
    @dataclass
    class Base:
        x: int
        s: str

        def f(self, y: int) -> int:
            z: int = self.x * y
            if z:
                print(self.s)
            return z
    
    Base_type_info = TypeInfo.from_py_type(Base)

    f_ast = ast.parse(textwrap.dedent(inspect.getsource(f))).body[0]
    assert isinstance(f_ast, ast.FunctionDef)
    scope = Scope(f_ast)

    type_info_dict = OrderedDict[TypeName, TypeInfo]()
    type_info_dict[TypeName(Identifier("int"))] = TypeInfo("int", None, int, [], [])
    type_info_dict[TypeName(Identifier("str"))] = TypeInfo("str", None, str, [], [])

    method_compiler = MethodCompiler(type_info_dict, Base_type_info)
    

    processor = Processor()

    text = "\n".join([])
    print(text)
    assembler = Assembler(list(tokenize(text)))
    assembler.assemble()

    IP = 0x40
    processor.memory.store_bytes(IP, assembler.buffer.getvalue())
    processor.registers.IP = IP

    for _ in range(20):
        processor.advance()
        print(processor.registers)

    assert processor.registers.A == value
