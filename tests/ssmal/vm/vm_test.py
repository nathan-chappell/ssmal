import json
import io
import typing as T

from pathlib import Path

import pytest

from ssmal.assemblers.token import Token
from ssmal.components.registers import Registers
from ssmal.instructions.processor_ops import HaltSignal
from ssmal.util.input_file_variant import InputFileVariant
from ssmal.vm1.vm import VM, VmConfig


class MultiException(Exception):
    exceptions: T.List[Exception]

    def __init__(self, exceptions: T.List[Exception], *args: object) -> None:
        super().__init__(*args)
        self.exceptions = exceptions


def _cleanup_paths(pathnames: T.List[str]):
    exceptions = []
    for pathname in pathnames:
        path = Path(pathname)
        try:
            if path.is_dir() and path.exists():
                path.rmdir()
            if path.exists():
                path.unlink()
        except Exception as e:
            exceptions.append(e)
    if exceptions:
        # raise MultiException(exceptions)
        _exception_types = [f"{e.__class__.__name__}: {e.message}" for e in exceptions]
        raise Exception("\n" + "\n".join(_exception_types))


@pytest.mark.parametrize(
    "input_file,expected",
    [
        ("""tests\\ssmal\\test_samples\\file_assembler\\include_bin_1\\ab.al""", b"\xab\x01\x02\x03\x04"),
        ("""tests\\ssmal\\test_samples\\file_assembler\\include_bin_2\\a\\ab.al""", b"\xab\x01\x02\x03\x04"),
        ("""tests\\ssmal\\test_samples\\file_assembler\\include_text_1\\ab.al""", b"\xab\x01\x02\x03\x04"),
        ("""tests\\ssmal\\test_samples\\file_assembler\\include_text_once_1\\ab.al""", b"\xab\x01\x02\x03\x04"),
    ],
)
def test_vm_assemble(input_file: str, expected: bytes):
    vm = VM()
    input_file_variant = InputFileVariant(input_file)

    try:
        vm.assemble(input_file_variant.assembler_filename)
        with open(input_file_variant.object_filename, "rb") as f:
            assert f.read()[: len(expected)] == expected
        with open(input_file_variant.debug_filename, "rt") as f:
            debug_info = json.load(f)
            assert debug_info["version"] == "0.0"
            symbol_table = {byte: Token(**token) for byte, token in debug_info["source_map"].items()}
            # I guess for now just assert no error occurs here...
    finally:
        _cleanup_paths([input_file_variant.object_filename, input_file_variant.debug_filename])


@pytest.mark.parametrize("input_file,expected", [("""tests\\ssmal\\test_samples\\vm\\hello_world_1\\hello_world.al""", "hello world!")])
def test_vm_pipeline(input_file: str, expected: str):
    cin = io.StringIO()
    cout = io.StringIO()
    config = VmConfig(cin=cin, cout=cout)
    vm = VM(config=config)
    input_file_variant = InputFileVariant(input_file)

    try:
        vm.assemble(input_file)
        assert Path(input_file_variant.object_filename).exists()
        assert Path(input_file_variant.debug_filename).exists()
        initial_registers = Registers(SP=0x80)
        vm.run(input_file_variant.object_filename, initial_registers=initial_registers)
        assert cout.getvalue() == expected
    finally:
        _cleanup_paths([input_file_variant.object_filename, input_file_variant.debug_filename])


# TODO: more tests to get all sys_io vectors
