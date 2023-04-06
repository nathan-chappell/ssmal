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
from ssmal.components.memory import Memory, MonitoredWrite
from ssmal.lang.ssmalloc.metadata.jit.codegen.allocator import TrivialAllocator
from ssmal.lang.ssmalloc.metadata.jit.codegen.label_maker import LabelMaker
from ssmal.lang.ssmalloc.metadata.jit.codegen.string_table import StringTable
from ssmal.processors.opcodes import opcode_map
from ssmal.instructions.processor_signals import HaltSignal
from ssmal.lang.ssmalloc.metadata.jit.jit_parser import JitParser
from ssmal.lang.ssmalloc.metadata.jit.strongly_typed_strings import Identifier, TypeName
from ssmal.processors.processor import Processor

from ssmal.lang.ssmalloc.metadata.jit.type_info import TypeInfo, int_type, str_type, type_cache
from ssmal.lang.ssmalloc.metadata.jit.codegen.scope import Scope
from ssmal.lang.ssmalloc.metadata.jit.codegen.method_compiler import MethodCompiler
from ssmal.util.ascii_safe_encode import ascii_safe_encode
from ssmal.util.hexdump_bytes import hexdump_bytes
from ssmal.util.writer.line_writer import LineWriter

import tests.ssmal.lang.ssmalloc.metadata.jit.codegen.samples.pair as pair_module
import tests.ssmal.lang.ssmalloc.metadata.jit.codegen.samples.triple as triple_module
import tests.ssmal.lang.ssmalloc.metadata.jit.codegen.samples.hello_world as hello_world_module


def get_pretty_mem(memory: Memory, start: int, count: int = 0x20) -> str:
    hex = memory.load_bytes(start, count).hex(bytes_per_sep=4, sep=" ")
    return f"{start:04x}: " + hex


@pytest.mark.parametrize("alloc_size", ((0x10), (0x20)))
def test_heap(alloc_size: int):
    string_table: StringTable = StringTable()
    type_dict: OrderedDict[TypeName, TypeInfo] = OrderedDict()
    label_maker: LabelMaker = LabelMaker()
    allocator = TrivialAllocator(string_table, type_dict, label_maker)
    line_writer: LineWriter = LineWriter()
    line_writer.write_line(f""".goto 0 ldai 0x{alloc_size:02x} cali $allocator.malloc halt""")
    allocator.create_heap(line_writer, 0x40)
    line_writer.write_line(""".align""")
    assembler: Assembler = Assembler(list(tokenize(line_writer.text)))
    assembler.assemble()
    processor: Processor = Processor()
    binary = assembler.buffer.getvalue()
    processor.memory.store_bytes(0, binary)
    processor.memory.dump()
    processor.registers.SP = len(binary)
    original_sp = processor.registers.SP
    try:
        for _ in range(5):
            for _ in range(10):
                IP = processor.registers.IP
                opcode = processor.memory.load_bytes(IP, 1)
                op = opcode_map.get(opcode, type(None)).__name__
                _op = int.from_bytes(opcode, "little", signed=False)
                _ip = IP & 0xFFFFFFE0
                print(f"{get_pretty_mem(processor.memory, _ip)} {processor.registers} | {op} (0x{_op:02x})")
                _ip_cursor_pos = IP % 0x20
                ip_cursor_line = " " * 6 + " " * (9 * (_ip_cursor_pos // 4) + 2 * (_ip_cursor_pos % 4)) + "^"
                print(ip_cursor_line)
                processor.advance()
            processor.memory.dump()
    except HaltSignal:
        processor.memory.dump()
        assert processor.registers.SP == original_sp
        assert processor.registers.IP == 0x0A
        assert processor.registers.A == 0x60
        assert processor.memory.load(0x40) == alloc_size
        # assert False
    else:
        assert False


@pytest.mark.parametrize(
    "module_name,expected_output", [("hello_world_module", "hello world"), ("pair_module", "3"), ("triple_module", "15")]
)
def test_object_creation(module_name: str, expected_output: bytes):
    type_cache.clear()
    jit_parser = JitParser()
    jit_parser.heap_size = 0x100
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

    def _listen_result_0(*args, **kwargs) -> None:
        assert jit_parser.processor is not None
        _bytes = jit_parser.processor.memory.load_bytes(jit_parser.processor.memory.load(jit_parser.processor.registers.SP - 4), 100)
        _bytes = _bytes[: _bytes.index(b"\x00")]
        _result = ascii_safe_encode(_bytes)
        raise HeardResult(_result)

    def _listen_result_1(*args, **kwargs) -> None:
        assert jit_parser.processor is not None
        value = jit_parser.processor.memory.load(jit_parser.processor.registers.SP - 4)
        _result = f"{value}"
        raise HeardResult(_result)

    jit_parser.processor.sys_vector[0] = _listen_result_0
    jit_parser.processor.sys_vector[1] = _listen_result_1

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
    # jit_parser.processor.memory.dump()
    last_source_line = ""

    with pytest.raises(HeardResult) as heard_result:
        for _ in range(400):
            # if ins % 20 == 0:
            #     # jit_parser.processor.memory.dump()
            #     print('*'*40)
            opcode = jit_parser.processor.memory.load_bytes(jit_parser.processor.registers.IP, 1)
            op = opcode_map.get(opcode, type(None)).__name__
            _op = int.from_bytes(opcode, "little", signed=False)

            IP = jit_parser.processor.registers.IP
            source_line_key = f"0x{IP:04x}"
            _mapping = _debug_info["source_map"].get(source_line_key, None) or {"line": -1}
            source_line = _mapping["line"]
            source_line = f"{source_line+1:03}: {_text_lines[source_line]}"
            if last_source_line != source_line:
                last_source_line = source_line
                print(source_line)

            _ip = IP & 0xFFFFFFE0
            print(f"{get_pretty_mem(jit_parser.processor.memory, _ip)} {jit_parser.processor.registers} | {op} (0x{_op:02x})")

            _ip_cursor_pos = IP % 0x20
            ip_cursor_line = " " * 6 + " " * (9 * (_ip_cursor_pos // 4) + 2 * (_ip_cursor_pos % 4)) + "^"
            print(ip_cursor_line)

            # print(f'{IP=}, {_ip=}, {_ip_cursor_pos=}')

            jit_parser.processor.advance()
            # print(f'{jit_parser.processor.registers}')
            if op in ("RETN", "STAb"):
                jit_parser.processor.memory.dump()

            if wrote_heap:
                print("### WROTE HEAP ###")
                print(
                    "\n".join(
                        get_pretty_mem(jit_parser.processor.memory, jit_parser.heap_start_addr + 0x20 * i, 0x20)
                        for i in range(jit_parser.heap_size // 0x20)
                    )
                )
                print("###")
            if wrote_stack:
                print("### WROTE HEAP ###")
                print("\n".join(get_pretty_mem(jit_parser.processor.memory, _initial_sp + 0x20 * i, 0x20) for i in range(2)))
                print("###")
            wrote_heap = wrote_stack = False
        else:
            assert False
    assert heard_result.value.zstr == expected_output
    # except HeardResult as result:
    #     assert result.zstr == expected_output
