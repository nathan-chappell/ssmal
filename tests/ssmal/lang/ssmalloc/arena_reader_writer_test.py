import pytest

from ssmal.lang.ssmalloc.arena import Arena
from ssmal.lang.ssmalloc.arena_reader_writer import ArenaReaderWriter


def test_arena_reader_writer():
    arena = Arena(memoryview(bytearray(0x10)))
    arena_rw = ArenaReaderWriter(arena)
    address = arena_rw.get_addr(0x4, 1)
    assert address == 0x08
    arena_rw.write_ptr(address, 0x12345678, offset=1)
    assert arena.view[0x0C:0x10].tobytes() == bytes.fromhex("78563412")
    assert arena_rw.read_ptr(address, offset=1) == 0x12345678
    arena_rw.get_view(0, 3)[0:3] = b"abc"
    assert arena_rw.get_view(0, 4).tobytes() == b"abc\x00"
    assert arena_rw.read_zstr(0) == "abc"


def test_arena_reader_writer_zstr_table():
    arena = Arena(memoryview(bytearray(0x40)))
    arena_rw = ArenaReaderWriter(arena)
    assert arena.malloc(1) == 0
    assert arena.index == 0x20
    zstr_table = b'foo\x00BAR\x00\x00'
    address = arena.embed(zstr_table)
    assert tuple(arena_rw.read_zstr_table(address)) == tuple(['foo', 'BAR'])
    assert arena.index == 0x40
    with pytest.raises(MemoryError):
        arena.embed(zstr_table)