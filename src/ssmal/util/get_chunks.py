from typing import Generator, overload


@overload
def get_chunks(_bytes: str, size: int = 40) -> Generator[str, None, None]:
    ...


@overload
def get_chunks(_bytes: bytes, size: int = 40) -> Generator[bytes, None, None]:
    ...


def get_chunks(_bytes: bytes | str, size: int = 40) -> Generator[bytes, None, None] | Generator[str, None, None]:
    n = len(_bytes) // size
    for i in range(n):
        yield _bytes[i * size : (i + 1) * size]
    remainder = (size - (len(_bytes) % size)) % size
    if remainder and isinstance(_bytes, bytes):
        yield _bytes[n * size :] + b"\x00" * remainder
