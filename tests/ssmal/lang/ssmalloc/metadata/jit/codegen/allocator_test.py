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
from ssmal.processors.opcodes import opcode_map
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

    build_dir = Path("tests/ssmal/lang/ssmalloc/metadata/jit/codegen/samples")
    with open(build_dir / "output.al", "w") as f:
        f.write(jit_parser.line_writer.text)
    with open(build_dir / "output.mem.bin", "wb") as f:
        f.write(jit_parser.processor.memory.buffer.getvalue())
    with open(build_dir / "output.mem.hex", "w") as f:
        f.write("\n".join(hexdump_bytes(jit_parser.processor.memory.buffer.getvalue())))

    _heap_mem = bytearray()
    _stack_mem = bytearray()
    _initial_sp = jit_parser.processor.memory.load(jit_parser.INITAL_SP_OFFSET)

    def _refresh_mem():
        assert jit_parser.processor is not None
        assert jit_parser.heap_start_addr is not None
        nonlocal _heap_mem, _stack_mem
        _newheap = jit_parser.processor.memory.load_bytes(jit_parser.heap_start_addr, jit_parser.heap_size)
        _newstack = jit_parser.processor.memory.load_bytes(_initial_sp, 0x200)
        
        if _newheap != _heap_mem:
            _heap_mem[:] = _newheap
            print(f'*** HEAP@(0x{jit_parser.heap_start_addr:04x})***')
            print('\n'.join(hexdump_bytes(_heap_mem)))
        
        if _newstack != _stack_mem:
            _stack_mem[:] = _newstack
            print(f'*** STACK@(0x{_initial_sp:04x})***')
            print('\n'.join(hexdump_bytes(_stack_mem)))

    for _ in range(50):
        opcode = jit_parser.processor.memory.load_bytes(jit_parser.processor.registers.IP, 1)
        op = opcode_map.get(opcode, type(None)).__name__
        print(f"{jit_parser.processor.registers} | {op}")
        jit_parser.processor.advance()
        _refresh_mem()
    assert False
