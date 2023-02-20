import json
import io
import typing as T
import sys

from dataclasses import dataclass, asdict
from functools import partial

import instructions.sys_io as sys_io

from assemblers.file_assembler import FileAssembler
from components.registers import Registers
from instructions.processor_ops import HaltException
from processors.processor import Processor

@dataclass
class VmConfig:
    cin: io.TextIOBase = sys.stdin
    cout: io.TextIOBase = sys.stdout


class VM:
    config: VmConfig
    processor: Processor

    DEBUG_INFO_VERSION = "0.0"
    OBJECT_FILE_EXT = "bin"
    DEBUG_FILE_EXT = "ssmdebug.json"

    def __init__(self, config: VmConfig = VmConfig()) -> None:
        self.config = config
        self.processor = Processor()

    def assemble(self, filename: str):
        """assembles input_file and outputs to input_file.bin"""
        file_assembler = FileAssembler()
        file_assembler.symbol_table["sys"] = b'\x80'
        file_assembler.assemble_file(filename)
        _bytes = file_assembler.buffer.getvalue()
        with open(f"{filename}.{self.OBJECT_FILE_EXT}", "wb") as f:
            f.write(_bytes)
        with open(f"{filename}.{self.DEBUG_FILE_EXT}", "w") as f:
            _debug_info = {offset: asdict(token) for offset, token in file_assembler.source_map.items()}
            json.dump({"version": self.DEBUG_INFO_VERSION, "source_map": _debug_info}, f)

    def run(self, filename: str, initial_registers: Registers = Registers()):
        """runs input_file as binary"""
        with open(filename, "rb") as f:
            _bytes = f.read()
        syscall = partial(sys_io.SYS, cout=self.config.cout, cin=self.config.cin)
        self.processor.update_syscall(syscall)
        self.processor.memory.store_bytes(0, _bytes)
        self.processor.registers = initial_registers
        try:
            while True:
                # breakpoint()
                self.processor.advance()
        except HaltException:
            pass