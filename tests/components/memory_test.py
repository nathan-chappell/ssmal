from tests import path_fix
path_fix()

import pytest

from components.memory import Memory

@pytest.mark.parametrize('value,address,expected', [
    (3,0,b'\x03\x00\x00\x00\x00\x00\x00\x00'),
    (-1,2,b'\x00\x00\xff\xff\xff\xff\x00\x00'),
])
def test_mem(value: int, address: int, expected: bytes):
    m = Memory(8)
    m.store(address, value)
    m.buffer.seek(0)
    assert m.buffer.read() == expected
    assert m.load(address) == value

    for i in range(1, len(expected)):
        assert m.load_bytes(0,i) == expected[:i]

@pytest.mark.parametrize('value,address,expected', [
    (3,0,b'\x03\x00\x00\x00'),
    (-1,2,b'\x00\x00\xff\xff\xff\xff'),
])
def test_mem_resize(value: int, address: int, expected: bytes):
    m = Memory()
    m.store(address, value)
    # Characterization:
    # it's not important that the size is now 256, just that we know what to expect
    m.buffer.seek(0)
    assert len(m.buffer.read()) == 256
    assert m.load(address) == value

@pytest.mark.parametrize('_bytes,address', [
    (b'\x03\x00\x00\x00', 2),
    (b'\x00\x00\xff\xff\xff\xff', 3),
])
def test_mem_load_bytes(_bytes: bytes, address: int):
    m = Memory()
    m.store_bytes(address, _bytes)
    assert m.load_bytes(address, len(_bytes)) == _bytes


# def test_mem_err():
#     m = Memory(8)
#     with pytest.raises(Exception):
#         m.store(6,6)