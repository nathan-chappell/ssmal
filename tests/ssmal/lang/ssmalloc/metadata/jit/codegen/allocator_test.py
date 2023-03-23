import ast
from collections import OrderedDict
from dataclasses import dataclass
import inspect
from pathlib import Path
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
from ssmal.util.hexdump_bytes import hexdump_bytes
from ssmal.util.writer.line_writer import LineWriter

import tests.ssmal.lang.ssmalloc.metadata.jit.codegen.samples.pair as pair_module


def test_object_creation():
    jit_parser = JitParser()
    jit_parser.parse_module(pair_module)
    jit_parser.compile()
    
    assert jit_parser.line_writer is not None
    assert jit_parser.assembly is not None
    assert jit_parser.processor is not None

    build_dir = Path('tests/ssmal/lang/ssmalloc/metadata/jit/codegen/samples')
    with open(build_dir / 'output.al', 'w') as f:
        f.write(jit_parser.line_writer.text)
    with open(build_dir / 'output.mem.bin', 'wb') as f:
        f.write(jit_parser.processor.memory.buffer.getvalue())
    with open(build_dir / 'output.mem.hex', 'w') as f:
        f.write("\n".join(hexdump_bytes(jit_parser.processor.memory.buffer.getvalue())))
