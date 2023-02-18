from tests import path_fix

path_fix()

import typing as T
import pytest

from util.get_chunks import get_chunks


@pytest.mark.parametrize(
    "_bytes,size,expected",
    [
        (b"0123456789", 5, [b"01234", b"56789"]),
        (b"0123456789", 2, [b"01", b"23", b"45", b"67", b"89"]),
        (b"0123456789", 3, [b"012", b"345", b"678", b"9\x00\x00"]),
    ],
)
def test_get_chunks(_bytes: bytes, size: int, expected: T.List[bytes]):
    assert list(get_chunks(_bytes, size=size)) == expected
