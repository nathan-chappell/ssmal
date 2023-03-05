import pytest

from ssmal.assemblers.token import Token
from ssmal.assemblers.tokenizer import tokenize

T = Token


@pytest.mark.parametrize(
    "input,expected",
    [
        ("", []),
        ("id.ef", [T("id", "id.ef", 0, 0)]),
        (".goto 0xe0", [T("dir", ".goto", 0, 0), T("xint", "0xe0", 0, 6)]),
        (
            "id.ef .dir 123 0x123 'foo ''bar' \"foo \\\"bar\" ; ;comment \n meow",
            # fmt: off
            [
                T("id",         "id.ef",            0, 0),
                T("dir",        ".dir",             0, 6),
                T("dint",       "123",              0, 11),
                T("xint",       "0x123",            0, 15),
                T("bstr",       "'foo ''bar'",      0, 21),
                T("zstr",       "\"foo \\\"bar\"",  0, 33),
                T("comment",    "; ;comment ",      0, 45),
                T("id",         "meow",             1, 1),
            ],
            # fmt: on
        ),
    ],
)
def test_tokenizer(input: str, expected: list[Token]):
    tokens = list(tokenize(input))
    assert tokens == expected
