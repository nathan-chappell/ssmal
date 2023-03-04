from pprint import pprint
import logging

import pytest

from ssmal.assemblers.tokenizer import tokenize
from ssmal.assemblers.assembler import Assembler
from ssmal.components.memory import MonitoredWrite
from ssmal.lang.tm.parser import parse_tm_transitions
from ssmal.lang.tm.compiler import TmCompiler, TransitionCompiler
from ssmal.processors.processor import Processor
from ssmal.util.writer.tm_assembler_writer import TmAssemblerWriter


def test_transition_compiler():
    tm_text = """
    A 1 B 2 R
    A 2 B 0 R
"""
    tm_assembler_writer = TmAssemblerWriter()
    transitions = list(parse_tm_transitions(tm_text))
    compiler = TransitionCompiler(tm_assembler_writer, "A", transitions)
    compiler.compile_transition()
    (tm_assembler_writer
        .newline().write_line('.goto  0xe0').label_state('B')
        .goto('A').comment("gangster")
    )
    print(tm_assembler_writer.text)
    assembler = Assembler(list(tokenize(tm_assembler_writer.text)))
    assembler.assemble()
    p = Processor()
    p.log.setLevel(logging.DEBUG)
    p.memory.store_bytes(0, assembler.buffer.getvalue())
    p.memory.dump()
    p.registers.SP = 0x60
    p.registers.B = 0x100
    
    p.memory.store(0x100, 1)
    p.memory.store(0x104, 1)
    p.memory.store(0x108, 2)

    p.memory.monitor(0x100, 0x10c)
    try:
        for _ in range(100): p.advance()
    except MonitoredWrite as monitor:
        assert p.memory.load(0x100) == 1
        monitor.finish_write()
        assert p.memory.load(0x100) == 2
    else:
        assert False, "expected a monitor"
    
    try:
        for _ in range(100): p.advance()
    except MonitoredWrite as monitor:
        assert p.memory.load(0x100) == 2
        assert p.memory.load(0x104) == 1
        monitor.finish_write()
        assert p.memory.load(0x104) == 2
    else:
        assert False, "expected a monitor"

    try:
        for _ in range(100): p.advance()
    except MonitoredWrite as monitor:
        assert p.memory.load(0x100) == 2
        assert p.memory.load(0x104) == 2
        assert p.memory.load(0x108) == 2
        monitor.finish_write()
        assert p.memory.load(0x108) == 0
    else:
        assert False, "expected a monitor"
