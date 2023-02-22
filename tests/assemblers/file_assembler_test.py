from tests import path_fix

path_fix()

from typing import List, Dict

import pytest

from assemblers.file_assembler import FileAssembler


@pytest.mark.parametrize(
    "input_file,expected",
    [
        ("""tests\\test_samples\\file_assembler\\include_bin_1\\ab.al""", b"\xab\x01\x02\x03\x04"),
        ("""tests\\test_samples\\file_assembler\\include_bin_2\\a\\ab.al""", b"\xab\x01\x02\x03\x04"),
        ("""tests\\test_samples\\file_assembler\\include_text_1\\ab.al""", b"\xab\x01\x02\x03\x04"),
        ("""tests\\test_samples\\file_assembler\\include_text_once_1\\ab.al""", b"\xab\x01\x02\x03\x04"),
    ],
)
def test_assembler(input_file: str, expected: bytes):
    assembler = FileAssembler()
    assembler.assemble_file(input_file)
    assert assembler.buffer.getvalue()[0 : len(expected)] == expected
