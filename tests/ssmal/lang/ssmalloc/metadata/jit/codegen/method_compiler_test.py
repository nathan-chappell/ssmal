import ast
from collections import OrderedDict
from dataclasses import dataclass
import inspect
import textwrap

import pytest

from ssmal.assemblers.tokenizer import tokenize
from ssmal.assemblers.assembler import Assembler
from ssmal.lang.ssmalloc.metadata.jit.jit_parser import JitParser
from ssmal.lang.ssmalloc.metadata.jit.strongly_typed_strings import Identifier, TypeName
from ssmal.processors.processor import Processor

from ssmal.lang.ssmalloc.metadata.jit.type_info import TypeInfo, int_type, str_type
from ssmal.lang.ssmalloc.metadata.jit.codegen.scope import Scope
from ssmal.lang.ssmalloc.metadata.jit.codegen.method_compiler import MethodCompiler


@pytest.fixture
def Base1_method_compiler():
    @dataclass
    class Base1:
        x: int
        s: str

        def f(self, y: int) -> int:
            z: int = self.x * y
            # if z:
            #     print(self.s)
            return z

    Base_type_info = TypeInfo.from_py_type(Base1)

    method_compiler = MethodCompiler(JitParser.builtin_type_info(), Base_type_info)
    yield method_compiler


def test_infer_type(Base1_method_compiler: MethodCompiler):
    f_ast = ast.parse(textwrap.dedent(inspect.getsource(Base1_method_compiler.self_type.methods[0].method))).body[0]
    assert isinstance(f_ast, ast.FunctionDef)
    body_0 = f_ast.body[0]
    assert isinstance(body_0, ast.AnnAssign)
    assert isinstance(body_0.value, ast.BinOp)
    Base1_method_compiler.reset_variable_types(Base1_method_compiler.self_type.methods[0])
    Base1_method_compiler.variable_types[Identifier("y")] = int_type
    assert Base1_method_compiler.infer_type(body_0.value).name == "int"


def test_assemble_basic_method(Base1_method_compiler: MethodCompiler):
    method = Base1_method_compiler.self_type.methods[0]
    Base1_method_compiler.reset_variable_types(method)
    assert len(Base1_method_compiler.variable_types) == 2
    assert Base1_method_compiler.variable_types[Identifier('self')] == Base1_method_compiler.self_type
    assert Base1_method_compiler.variable_types[Identifier('y')] == int_type
    assembly_code = "\n".join(Base1_method_compiler.compile_method(method))
    indent=0
    for ins in Base1_method_compiler.compile_method(method):
        if '|>' in ins:
            indent += 1
        elif '|<' in ins:
            indent -= 1
        print('  '*indent + ins)

    assembler = Assembler(list(tokenize(assembly_code)))
    assembler.assemble()

    assert False