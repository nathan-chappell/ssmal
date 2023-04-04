import ast
import inspect
import json
import textwrap

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

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
from ssmal.util.ascii_safe_encode import ascii_safe_encode
from ssmal.util.hexdump_bytes import hexdump_bytes
from ssmal.util.writer.line_writer import LineWriter

import tests.ssmal.lang.ssmalloc.metadata.jit.codegen.samples.pair as pair_module
import tests.ssmal.lang.ssmalloc.metadata.jit.codegen.samples.hello_world as hello_world_module


@pytest.mark.parametrize("module_name,expected_output", [
    ("hello_world_module", "hello world"),
    ("pair_module", "3"),
])
def test_object_creation(module_name: str, expected_output: bytes):
    jit_parser = JitParser()
    # jit_parser.parse_module(pair_module)
    _module = globals().get(module_name)
    assert _module is not None
    jit_parser.parse_module(_module)
    jit_parser.compile()

    assert jit_parser.debug_info is not None
    assert jit_parser.line_writer is not None
    assert jit_parser.assembly is not None
    assert jit_parser.processor is not None

    class HeardResult(Exception):
        zstr: str

        def __init__(self, zstr: str, *args: object) -> None:
            super().__init__(*args)
            self.zstr = zstr

    def _listen_result(*args, **kwargs) -> None:
        assert jit_parser.processor is not None
        _bytes = jit_parser.processor.memory.load_bytes(jit_parser.processor.memory.load(jit_parser.processor.registers.SP - 4), 100)
        _bytes = _bytes[: _bytes.index(b"\x00")]
        _result = ascii_safe_encode(_bytes)
        raise HeardResult(_result)

    jit_parser.processor.sys_vector[0] = _listen_result

    build_dir = Path("tests/ssmal/lang/ssmalloc/metadata/jit/codegen/samples")
    _text = jit_parser.line_writer.text
    _text_lines = _text.split("\n")
    _text_lines.append("<NO LINE>")
    with open(build_dir / "output.al", "w") as f:
        f.write(_text)
    with open(build_dir / "output.mem.bin", "wb") as f:
        f.write(jit_parser.processor.memory.buffer.getvalue())
    with open(build_dir / "output.mem.hex", "w") as f:
        f.write("\n".join(hexdump_bytes(jit_parser.processor.memory.buffer.getvalue())))
    with open(build_dir / "output.debug_info.json", "w") as f:
        f.write(jit_parser.debug_info)
        _debug_info = json.loads(jit_parser.debug_info)

    _initial_sp = jit_parser.processor.memory.load(jit_parser.INITAL_SP_OFFSET)

    def get_pretty_mem(start: int, count: int = 0x20) -> str:
        assert jit_parser.processor is not None
        hex = jit_parser.processor.memory.load_bytes(start, count).hex(bytes_per_sep=4, sep=" ")
        return f"{start:04x}: " + hex

    wrote_heap: bool = False
    wrote_stack: bool = False

    def _address_in_heap(addr: int) -> bool:
        _start = jit_parser.heap_start_addr
        assert _start is not None
        return _start <= addr <= _start + jit_parser.heap_size

    def _address_in_stack(addr: int) -> bool:
        return _initial_sp <= addr

    def on_monitor(monitored_write: MonitoredWrite) -> None:
        nonlocal wrote_heap, wrote_stack
        wrote_heap = _address_in_heap(monitored_write.address)
        wrote_stack = _address_in_stack(monitored_write.address)
        print(f"[MONITOR] {wrote_heap=} {wrote_stack=} {monitored_write.address=}")

    jit_parser.processor.memory.monitor_action = on_monitor

    assert jit_parser.heap_start_addr is not None
    jit_parser.processor.memory.dump()
    last_source_line = ""

    try:
        for _ in range(105):
            opcode = jit_parser.processor.memory.load_bytes(jit_parser.processor.registers.IP, 1)
            op = opcode_map.get(opcode, type(None)).__name__
            _op = int.from_bytes(opcode, "little", signed=False)
            IP = jit_parser.processor.registers.IP
            source_line_key = f"0x{IP+1:04x}"
            _mapping = _debug_info["source_map"].get(source_line_key, None) or {"line": -1}
            source_line = _mapping["line"]
            source_line = f"{source_line+1:03}: {_text_lines[source_line]}"
            if last_source_line != source_line:
                last_source_line = source_line
                print(source_line)

            _ip = IP & 0xFFFFFFE0
            print(f"{get_pretty_mem(_ip)} {jit_parser.processor.registers} | {op} (0x{_op:02x})")

            _ip_cursor_pos = IP % 0x20
            ip_cursor_line = " " * 6 + " " * (9 * (_ip_cursor_pos // 4) + 2 * (_ip_cursor_pos % 4)) + "^"
            print(ip_cursor_line)

            # print(f'{IP=}, {_ip=}, {_ip_cursor_pos=}')

            jit_parser.processor.advance()
            # print(f'{jit_parser.processor.registers}')

            if wrote_heap:
                print("### WROTE HEAP ###")
                print("\n".join(get_pretty_mem(jit_parser.heap_start_addr + 0x20 * i, 0x20) for i in range(jit_parser.heap_size // 0x20)))
                print("###")
            if wrote_stack:
                print("### WROTE HEAP ###")
                print("\n".join(get_pretty_mem(_initial_sp + 0x20 * i, 0x20) for i in range(2)))
                print("###")
            wrote_heap = wrote_stack = False
        else:
            assert False
    except HeardResult as result:
        assert result.zstr == expected_output