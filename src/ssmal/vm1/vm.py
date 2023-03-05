import json
import io

import sys
import logging

from dataclasses import dataclass, asdict
from pprint import pprint
from typing import TextIO

from ssmal.assemblers.file_assembler import FileAssembler
from ssmal.components.registers import Registers
from ssmal.instructions.processor_ops import HaltSignal
from ssmal.lang.tm.compiler import TmCompiler
from ssmal.processors.processor import Processor
from ssmal.util.hexdump_bytes import hexdump_bytes
from ssmal.util.input_file_variant import InputFileVariant
from ssmal.vm1.sys_io import SysIO

log = logging.getLogger(__name__)


def _ensure_input_file_variant(_input_file: str | InputFileVariant) -> InputFileVariant:
    if isinstance(_input_file, str):
        return InputFileVariant(_input_file)
    else:
        return _input_file


@dataclass
class VmConfig:
    cin: TextIO = sys.stdin
    cout: TextIO = sys.stdout
    initial_registers: Registers = Registers()
    trace: bool = False


class VM:
    config: VmConfig
    file_assembler: FileAssembler
    log = log
    processor: Processor
    sys_io: SysIO

    max_steps = 500

    DEBUG_INFO_VERSION = "0.0"
    OBJECT_FILE_EXT = "bin"
    DEBUG_FILE_EXT = "ssmdebug.json"

    def __init__(self, config: VmConfig = VmConfig()) -> None:
        self.config = config
        self.processor = Processor()
        self.sys_io = SysIO()
        self.configure()
        self.file_assembler = FileAssembler()

    def configure(self):
        self.sys_io.bind(cin=self.config.cin, cout=self.config.cout)
        self.processor.sys_vector = self.sys_io.sys_vector
        self.processor.registers = self.config.initial_registers

    def assemble(self, _input_file: str | InputFileVariant):
        """assembles input_file and outputs to input_file.bin"""
        input_file = _ensure_input_file_variant(_input_file)
        self.file_assembler = FileAssembler()
        self.file_assembler.assemble_file(input_file.assembler_filename)
        _bytes = self.file_assembler.buffer.getvalue()
        with open(input_file.object_filename, "wb") as f:
            f.write(_bytes)
        with open(input_file.debug_filename, "w") as f:
            _debug_info = {offset: asdict(token) for offset, token in self.file_assembler.source_map.items()}
            _labels = {
                label.token.value: f"{label.address:08x}" for label in self.file_assembler.labels.values() if label.token is not None
            }
            json.dump({"version": self.DEBUG_INFO_VERSION, "labels": _labels, "source_map": _debug_info}, f, indent=2)

    def compile_tm_lang(self, _input_file: str | InputFileVariant):
        """compiles input_file and outputs to input_file.al"""
        input_file = _ensure_input_file_variant(_input_file)
        tm_compiler = TmCompiler()
        tm_compiler.compile_file(input_file.tm_filename)
        with open(input_file.assembler_filename, "w") as f:
            f.write(tm_compiler.assembly)

    def start(self):
        if self.config.trace:
            self.log.setLevel(logging.DEBUG)

        _MAX_STEPS = self.max_steps

        self.log.debug("PROCESSOR START")
        self.log.debug(self.processor.registers)
        if self.config.trace:
            self.log.debug("\n" + "\n".join(hexdump_bytes(self.processor.memory.load_bytes(0, 0x100))))
        try:
            # while True:
            for _ in range(_MAX_STEPS):
                self.processor.advance()
                self.log.debug(self.processor.registers)
        except HaltSignal:
            if self.config.trace:
                print("RECEIVED HALT")
                pprint(self.processor.registers)
                # fmt: off
                import ipdb; ipdb.set_trace()
                ...
                # fmt: on
            pass
        except Exception as e:
            if self.config.trace:
                print(e)
                # fmt: off
                import ipdb; ipdb.set_trace()
                ...
                # fmt: on

        if self.config.trace:
            print("\n".join(hexdump_bytes(self.processor.memory.load_bytes(0, 0x100))))
            pprint(self.processor.registers)

    def run_tm(self, input_file: InputFileVariant, input: str) -> None:
        with open(input_file.object_filename, "br") as f:
            _program_bytes = f.read()
        _end_of_program = len(_program_bytes)
        _end_of_stack = _end_of_program + 4  # we only need a stack of size 4...
        _beginning_of_input = _end_of_stack
        _end_of_input = _end_of_stack + len(input)

        _one_bytes = (1).to_bytes(4, "little")
        _two_bytes = (2).to_bytes(4, "little")

        _input_bytes = b"".join([_one_bytes if c == "1" else _two_bytes for c in input])

        self.processor.memory.store_bytes(0, _program_bytes)
        self.processor.memory.store_bytes(_end_of_stack, _input_bytes)
        self.processor.memory.store(_end_of_input, 0)  # probably not strictly necessary...
        self.processor.memory.monitor(0, _end_of_program)
        self.processor.registers.SP = _end_of_program
        self.processor.registers.B = _beginning_of_input

        self.start()

    def run(self, _input_file: str | InputFileVariant, initial_registers: Registers = Registers()):
        """runs input_file as binary"""
        input_file = _ensure_input_file_variant(_input_file)
        with open(input_file.object_filename, "rb") as f:
            _program_bytes = f.read()
        self.processor.memory.store_bytes(0, _program_bytes)

        self.start()
