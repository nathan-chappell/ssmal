import typing as T


def get_chunks(_bytes: bytes, size: int = 40) -> T.Generator[bytes, None, None]:
    n = len(_bytes) // size
    for i in range(n):
        yield _bytes[i * size : (i + 1) * size]
    remainder = (size - (len(_bytes) % size)) % size
    if remainder:
        yield _bytes[n * size :] + b"\x00" * remainder
