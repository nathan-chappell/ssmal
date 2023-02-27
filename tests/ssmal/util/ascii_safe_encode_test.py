import pytest

from ssmal.util.ascii_safe_encode import ascii_safe_encode


def test_ascii_safe_encode():
    _bytes = b"\x03abcd\xff"
    assert ascii_safe_encode(_bytes) == ".abcd."
    assert ascii_safe_encode(_bytes, default_char="_") == "_abcd_"
