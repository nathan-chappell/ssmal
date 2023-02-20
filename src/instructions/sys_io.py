import io

from components.memory import Memory
from components.registers import Registers

from util.ascii_safe_encode import ascii_safe_encode
from util.hexdump_bytes import hexdump_bytes

PTOPz = 0  # print top of stack as null-terminated string
PTOPi = 1  # print top of stack as decimal integer
PTOPx = 2  # print top of stack as 4-byte int in hex (le - probably)
PREG = 3  # print registers
PMEM = 4  # dump memory


def SYS(r: Registers, m: Memory, cin: io.TextIOBase, cout: io.TextIOBase) -> None:
    MAX_ZSTRLEN = 0x100
    if r.A == PMEM:
        start = m.load(r.SP - 8, 4)
        count = m.load(r.SP - 4, 4)
        cout.write("\n".join(hexdump_bytes(m.load_bytes(start, count))))
    elif r.A == PREG:
        cout.write(str(r))
    elif r.A == PTOPz:
        start = m.load(r.SP - 4, 4)
        buffer = m.load_bytes(start, MAX_ZSTRLEN)
        _bytes = buffer[0 : buffer.find(0)]
        cout.write(ascii_safe_encode(_bytes))
    elif r.A == PTOPi:
        i = m.load(r.SP - 4, 4)
        cout.write(f"{i}")
    elif r.A == PTOPx:
        i = m.load(r.SP - 4, 4)
        cout.write(f"0x{i:08x}")
    else:
        raise Exception(f"unknown syscall: 0x{r.A:x}")
    
    r.IP += 1
