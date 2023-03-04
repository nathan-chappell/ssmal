import pytest

from ssmal.components.memory import Memory, MonitoredWrite


@pytest.mark.parametrize(
    "value,address,expected", [(3, 0, b"\x03\x00\x00\x00\x00\x00\x00\x00"), (-1, 2, b"\x00\x00\xff\xff\xff\xff\x00\x00")]
)
def test_mem(value: int, address: int, expected: bytes):
    m = Memory(8)
    m.store(address, value)
    m.buffer.seek(0)
    assert m.buffer.read() == expected
    assert m.load(address) == value

    for i in range(1, len(expected)):
        assert m.load_bytes(0, i) == expected[:i]


@pytest.mark.parametrize("value,address,expected", [(3, 0, b"\x03\x00\x00\x00"), (-1, 2, b"\x00\x00\xff\xff\xff\xff")])
def test_mem_resize(value: int, address: int, expected: bytes):
    m = Memory()
    m.store(address, value)
    # Characterization:
    # it's not important that the size is now 256, just that we know what to expect
    m.buffer.seek(0)
    assert len(m.buffer.read()) == 256
    assert m.load(address) == value


@pytest.mark.parametrize("_bytes,address", [(b"\x03\x00\x00\x00", 2), (b"\x00\x00\xff\xff\xff\xff", 3)])
def test_mem_load_bytes(_bytes: bytes, address: int):
    m = Memory()
    m.store_bytes(address, _bytes)
    assert m.load_bytes(address, len(_bytes)) == _bytes


def test_mem_monitor():
    m = Memory()
    m.store_bytes(0, b"\x01\x23\x45\x67\x89\xab\xcd\xef")
    r1 = (3, 7)
    a1, b1 = 1, (2).to_bytes(4, "little")
    a2, b2 = 5, b"\xcc\xdd"
    m.watch_region(*r1)

    try:
        m.store_bytes(0, b"\x00")
    except MonitoredWrite as monitor:
        assert False, "region not monitored"

    try:
        m.store(a1, 2)
    except MonitoredWrite as monitor:
        assert m.load(a1, signed=False) == 0x89674523
        monitor.finish_write()
        assert m.load(a1, signed=False) == 0x02
    else:
        assert False, "expected throw"

    try:
        m.store_bytes(a2, b2)
    except MonitoredWrite as monitor:
        assert m.load_bytes(a2, len(b2)) == b"\xab\xcd"
        monitor.finish_write()
        assert m.load_bytes(a2, len(b2)) == b2
    else:
        assert False, "expected throw"


# def test_mem_err():
#     m = Memory(8)
#     with pytest.raises(Exception):
#         m.store(6,6)
