import typing as T
import json
from dataclasses import dataclass, asdict

from assemblers.file_assembler import FileAssembler


class VmConfig:
    ...


class VM:
    config: VmConfig
    _DEBUG_INFO_VERSION = "0.0"

    def __init__(self, config: VmConfig = VmConfig()) -> None:
        self.config = config

    def assemble(self, filename: str):
        """assembles input_file and outputs to input_file.bin"""
        file_assembler = FileAssembler()
        file_assembler.assemble_file(filename)
        _bytes = file_assembler.buffer.getvalue()
        with open(f"{filename}.bin", "wb") as f:
            f.write(_bytes)
        with open(f"{filename}.ssmdebug.json", "w") as f:
            _debug_info = {offset: asdict(token) for offset, token in file_assembler.debug_info.items()}
            json.dump({"version": self._DEBUG_INFO_VERSION, "debug_info": _debug_info}, f)

    def run(self):
        """runs input_file as binary"""
        ...
