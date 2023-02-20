from tests import path_fix

path_fix()

import json
import io
import typing as T

from contextlib import contextmanager
from pathlib import Path

import pytest

from assemblers.token import Token
from instructions.processor_ops import HaltException
from vm import VM, VmConfig


class MultiException(Exception):
    exceptions: T.List[Exception]

    def __init__(self, exceptions: T.List[Exception], *args: object) -> None:
        super().__init__(*args)
        self.exceptions = exceptions


def _cleanup_paths(pathnames: T.List[str]) -> T.Generator[None, None, None]:
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
    "inputFile,expected",
    [
        ("""tests\\test_samples\\file_assembler\\include_bin_1\\ab.al""", b"\xab\x01\x02\x03\x04"),
        ("""tests\\test_samples\\file_assembler\\include_bin_2\\a\\ab.al""", b"\xab\x01\x02\x03\x04"),
        ("""tests\\test_samples\\file_assembler\\include_text_1\\ab.al""", b"\xab\x01\x02\x03\x04"),
        ("""tests\\test_samples\\file_assembler\\include_text_once_1\\ab.al""", b"\xab\x01\x02\x03\x04"),
    ],
)
def test_vm_assemble(inputFile: str, expected: bytes):
    vm = VM()
    _obj_filename = f"{inputFile}.{vm.OBJECT_FILE_EXT}"
    _dbg_filename = f"{inputFile}.{vm.DEBUG_FILE_EXT}"

    try:
        vm.assemble(inputFile)
        with open(_obj_filename, "rb") as f:
            assert f.read()[: len(expected)] == expected
        with open(_dbg_filename, "rt") as f:
            debug_info = json.load(f)
            assert debug_info["version"] == "0.0"
            symbol_table = {byte: Token(**token) for byte, token in debug_info["source_map"].items()}
            # I guess for now just assert no error occurs here...
    finally:
        _cleanup_paths([_obj_filename, _dbg_filename])
        
        
@pytest.mark.parametrize(
    "inputFile,expected",
    [
        ("""tests\\test_samples\\vm\\hello_world_1\\hello_world.al""", "Hello World"),
    ],
)
def test_vm_pipeline(inputFile: str, expected: str):
    cin = io.StringIO()
    cout = io.StringIO()
    config = VmConfig(cin=cin, cout=cout)
    vm = VM(config=config)
    
    _obj_filename = f"{inputFile}.{vm.OBJECT_FILE_EXT}"
    _dbg_filename = f"{inputFile}.{vm.DEBUG_FILE_EXT}"

    try:
        vm.assemble(inputFile)
        assert Path(_obj_filename).exists()
        assert Path(_dbg_filename).exists()
        try:
            vm.run(_obj_filename)
        except HaltException:
            breakpoint()
            assert cout.getvalue() == expected
        else:
            assert False
    finally:
        _cleanup_paths([_obj_filename, _dbg_filename])
