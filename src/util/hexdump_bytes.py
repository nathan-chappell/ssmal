import typing as T

from util.get_chunks import get_chunks

def _ascii_safe_encode(_bytes: bytes):
    s = ''
    _default_char = '.'
    for _byte in _bytes:
        c = chr(_byte)
        if c.isprintable() and c.isascii():
            s += c
        else:
            s += _default_char
    return s

def hexdump_bytes(_bytes: bytes) -> T.Generator[str, None, None]:
    _size = 0x20
    for i,chunk in enumerate(get_chunks(_bytes, size=_size)):
        addr_str = f'{i * _size:04x}'
        chunk_str = ' '.join([_b.hex() for _b in get_chunks(chunk, size=0x04)])
        ascii_str = _ascii_safe_encode(chunk)
        yield f'{addr_str}: {chunk_str} | {ascii_str}'
