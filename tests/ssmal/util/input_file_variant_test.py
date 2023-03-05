import pytest

from ssmal.util.input_file_variant import InputFileVariant


@pytest.mark.parametrize("variant_name", ["assembler", "debug", "object", "tm"])
def test_input_file(variant_name: str):
    filename = "foo"
    _suffix = getattr(InputFileVariant, f"{variant_name}_file_suffix")
    input_file = InputFileVariant(filename + _suffix)
    assert getattr(input_file, f"is_{variant_name}_file")
    assert input_file.assembler_filename == filename + InputFileVariant.assembler_file_suffix
    assert input_file.debug_filename == filename + InputFileVariant.debug_file_suffix
    assert input_file.object_filename == filename + InputFileVariant.object_file_suffix
    assert input_file.tm_filename == filename + InputFileVariant.tm_file_suffix
