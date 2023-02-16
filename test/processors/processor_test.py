import sys

sys.path.append('C:\\Users\\natha\\programming\\py\\ssmal\\src')

import pytest

from processors.processor import Processor


@pytest.mark.parametrize(
    "op,A,B,expected",
    [
        (b'\x10', 3, 4, 7),
        (b'\x11', 3, 4, -1),
        (b'\x12', 3, 4, 12),
        (b'\x13', 3, 4, 0),
    ],
)
def test_opsB(op: bytes, A: int, B: int, expected: int):
    p = Processor()
    p.memory.store_bytes(0, op)
    p.registers.A = A
    p.registers.B = B
    p.advance()
    assert p.registers.A == expected
