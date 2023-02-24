from typing import List, Dict

import pytest

from ssmal.assemblers.file_assembler import FileAssembler
from ssmal.assemblers.errors import UnexpectedTokenError


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


@pytest.mark.parametrize(
    "input_file,error_type",
    [
        ("""tests\\test_samples\\file_assembler\\unexpected_token\\include_arg.al""", UnexpectedTokenError),
        ("""tests\\test_samples\\file_assembler\\unexpected_token\\filename.al""", UnexpectedTokenError),
    ],
)
def test_assembler_error(input_file: str, error_type: type):
    assembler = FileAssembler()
    with pytest.raises(error_type):
        assembler.assemble_file(input_file)
