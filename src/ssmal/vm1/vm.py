import json
import io

import sys

from dataclasses import dataclass, asdict
from functools import partial
from typing import TextIO

from ssmal.assemblers.file_assembler import FileAssembler
from ssmal.components.registers import Registers
from ssmal.instructions.processor_ops import HaltSignal
from ssmal.processors.processor import Processor
from ssmal.util.input_file_variant import InputFileVariant
from ssmal.vm1.sys_io import SysIO


@dataclass
class VmConfig:
    cin: TextIO = sys.stdin
    cout: TextIO = sys.stdout
    initial_registers: Registers = Registers()


class VM:
    config: VmConfig
    processor: Processor
    sys_io: SysIO

    DEBUG_INFO_VERSION = "0.0"
    OBJECT_FILE_EXT = "bin"
    DEBUG_FILE_EXT = "ssmdebug.json"

    def __init__(self, config: VmConfig = VmConfig()) -> None:
        self.config = config
        self.processor = Processor()
        self.sys_io = SysIO()
        self.configure()

    def configure(self):
        self.sys_io.bind(cin=self.config.cin, cout=self.config.cout)
        self.processor.sys_vector = self.sys_io.sys_vector
        self.processor.registers = self.config.initial_registers

    def assemble(self, filename: str):
        """assembles input_file and outputs to input_file.bin"""
        input_file = InputFileVariant(filename)
        file_assembler = FileAssembler()
        file_assembler.assemble_file(input_file.assembler_filename)
        _bytes = file_assembler.buffer.getvalue()
        with open(input_file.object_filename, "wb") as f:
            f.write(_bytes)
        with open(input_file.debug_filename, "w") as f:
            _debug_info = {offset: asdict(token) for offset, token in file_assembler.source_map.items()}
            json.dump({"version": self.DEBUG_INFO_VERSION, "source_map": _debug_info}, f)

    def run(self, filename: str, initial_registers: Registers = Registers()):
        """runs input_file as binary"""
        with open(filename, "rb") as f:
            _bytes = f.read()
        self.processor.memory.store_bytes(0, _bytes)
        try:
            while True:
                self.processor.advance()
        except HaltSignal:
            pass
