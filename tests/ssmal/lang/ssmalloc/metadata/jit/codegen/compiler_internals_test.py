import ast
import inspect
import textwrap

import pytest

from ssmal.assemblers.tokenizer import tokenize
from ssmal.assemblers.assembler import Assembler
from ssmal.processors.processor import Processor

from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_internals import CompilerInternals


def test_compiler_internals():
    ci = CompilerInternals()

    s, s_addr = 'foobar', 0x40
    l, l_addr = 'l1', 0x18

    text = f"""
    .goto {s_addr} {ci.ZSTR(s)}
    .goto {l_addr} {ci.MARK_LABEL(l)}
    .goto {0} bri {ci.GOTO_LABEL(l)}
"""

    print(text)
    assembler = Assembler(list(tokenize(text)))
    assembler.assemble()
    IP = 0x00
    processor = Processor()
    processor.memory.store_bytes(IP, assembler.buffer.getvalue())
    processor.registers.IP = IP

    for _ in range(2):
        processor.advance()
        print(processor.registers)
    assert processor.registers.IP == l_addr
    assert processor.memory.load_bytes(s_addr, len(s) + 1) == bytes(s, encoding='ascii') + b'\x00'
