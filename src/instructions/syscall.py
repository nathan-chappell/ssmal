import io

import instructions.syscalls as V

from components.memory import Memory
from components.registers import Registers

from util.ascii_safe_encode import ascii_safe_encode
from util.hexdump_bytes import hexdump_bytes


def SYS(r: Registers, m: Memory, cin: io.TextIOBase, cout: io.TextIOBase) -> None:
    MAX_ZSTRLEN = 0x100

    if r.A == V.PMEM:
        start = m.load(r.SP - 8, 4)
        count = m.load(r.SP - 4, 4)
        cout.write("\n".join(hexdump_bytes(m.load_bytes(start, count))))
    elif r.A == V.PREG:
        cout.write(str(r))
    elif r.A == V.PTOPz:
        start = m.load(r.SP - 4, 4)
        buffer = m.load_bytes(start, MAX_ZSTRLEN)
        _bytes = buffer[0 : buffer.find(0)]
        cout.write(ascii_safe_encode(_bytes))
    elif r.A == V.PTOPi:
        i = m.load(r.SP - 4, 4)
        cout.write(f"{i}")
    elif r.A == V.PTOPx:
        i = m.load(r.SP - 4, 4)
        cout.write(f"{i:08x}")
    else:
        raise Exception(f"unknown syscall: 0x{r.A:x}")
