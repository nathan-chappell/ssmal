from util.get_chunks import get_chunks


def ascii_safe_encode(_bytes: bytes):
    s = ""
    _default_char = "."
    for _byte in _bytes:
        c = chr(_byte)
        if c.isprintable() and c.isascii():
            s += c
        else:
            s += _default_char
    return s
