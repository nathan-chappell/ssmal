import json
import io
import typing as T
import sys

from dataclasses import dataclass, asdict
from functools import partial

import instructions.sys_io as sys_io

from assemblers.file_assembler import FileAssembler
from components.registers import Registers
from instructions.processor_ops import HaltSignal
from processors.processor import Processor
from util.input_file_variant import InputFileVariant


@dataclass
class VmConfig:
    cin: T.TextIO = sys.stdin
    cout: T.TextIO = sys.stdout
    initial_registers: Registers = Registers()


class VM:
    config: VmConfig
    processor: Processor

    DEBUG_INFO_VERSION = "0.0"
    OBJECT_FILE_EXT = "bin"
    DEBUG_FILE_EXT = "ssmdebug.json"

    def __init__(self, config: VmConfig = VmConfig()) -> None:
        self.config = config
        self.processor = Processor()
        self.configure()

    def configure(self):
        self.processor.sys_io.cin = self.config.cin
        self.processor.sys_io.cout = self.config.cout
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


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--compile", action="store_true")
    parser.add_argument("-r", "--run", action="store_true")
    parser.add_argument("filename")
    args = parser.parse_args(sys.argv[1:])

    filename = T.cast(str, args.filename)

    vm = VM()
    if args.compile:
        if not filename.endswith(InputFileVariant.suffix_map.assembler_file_suffix):
            raise RuntimeError(f"{filename} does not look like a ssmal assembler file - missing .al extension")
        vm.assemble(filename)
    elif args.run:
        if not filename.endswith(InputFileVariant.suffix_map.object_file_suffix):
            raise RuntimeError(f"{filename} does not look like a ssmal object file - missing .bin extension")
        vm.run(filename)
    else:
        raise RuntimeError(f"neither -compile nor -run specified")
