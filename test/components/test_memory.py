import sys
sys.path.append('D:\\programming\\py\\ssmal\\src')

import pytest

from components.memory import Memory

@pytest.mark.parametrize('value,address,expected', [
    (3,0,b'\x03\x00\x00\x00\x00\x00\x00\x00'),
    (-1,2,b'\x00\x00\xff\xff\xff\xff\x00\x00'),
])
def test_mem(value: int, address: int, expected: bytes):
    m = Memory(8)
    m.store(address, value)
    assert m.buffer.getvalue() == expected
    assert m.load(address) == value
