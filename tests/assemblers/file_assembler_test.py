from tests import path_fix

path_fix()

from typing import List, Dict

import pytest

from assemblers.file_assembler import FileAssembler

@pytest.mark.parametrize(
    "inputFile,expected",
    [
        (
            """tests\\test_samples\\file_assembler\\test_include_1\\ab.al""",
            b"\xab\xcd",
        ),
    ],
)
def test_assembler(inputFile: str, expected: bytes):
    assembler = FileAssembler()
    assembler.assemble_file(inputFile)
    assert assembler.buffer.getvalue()[0 : len(expected)] == expected
