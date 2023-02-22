import typing as T

from ssmal.util.get_chunks import get_chunks
from ssmal.util.ascii_safe_encode import ascii_safe_encode


def hexdump_bytes(_bytes: bytes) -> T.Generator[str, None, None]:
    _size = 0x20
    for i, chunk in enumerate(get_chunks(_bytes, size=_size)):
        addr_str = f"{i * _size:04x}"
        chunk_str = " ".join([_b.hex() for _b in get_chunks(chunk, size=0x04)])
        ascii_str = ascii_safe_encode(chunk)
        yield f"{addr_str}: {chunk_str} | {ascii_str}"
