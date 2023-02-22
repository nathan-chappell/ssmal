import io
import typing as T
from functools import partial

from ssmal.components.memory import Memory
from ssmal.components.registers import Registers
from ssmal.processors.processor import TOp

from ssmal.util.ascii_safe_encode import ascii_safe_encode
from ssmal.util.hexdump_bytes import hexdump_bytes

PTOPz = 0  # print top of stack as null-terminated string
PTOPi = 1  # print top of stack as decimal integer
PTOPx = 2  # print top of stack as 4-byte int in hex (le - probably)
PREG = 3  # print registers
PMEM = 4  # dump memory


class SysIO:
    cin: T.Optional[T.TextIO] = None
    cout: T.Optional[T.TextIO] = None
    sys_vector: T.Dict[int, TOp]

    max_zstrlen: int = 0x100

    def __init__(self):
        def _nop(*args, **kwargs):
            pass

        self.sys_vector = {
            PTOPz: _nop,
            PTOPi: _nop,
            PTOPx: _nop,
            PREG: _nop,
            PMEM: _nop,
        }

    def bind(self, cin: T.Optional[T.TextIO] = None, cout: T.Optional[T.TextIO] = None):
        if cin is not None:
            self.cin = cin
        if cout is not None:
            self.cout = cout

        self.sys_vector = {
            PTOPz: partial(print_top_z, cin=self.cin, cout=self.cout, max_zstrlen=self.max_zstrlen),
            PTOPi: partial(print_top_z, cin=self.cin, cout=self.cout, max_zstrlen=self.max_zstrlen),
            PTOPx: partial(print_top_z, cin=self.cin, cout=self.cout, max_zstrlen=self.max_zstrlen),
            PREG: partial(print_top_z, cin=self.cin, cout=self.cout, max_zstrlen=self.max_zstrlen),
            PMEM: partial(print_top_z, cin=self.cin, cout=self.cout, max_zstrlen=self.max_zstrlen),
        }


def print_top_z(r: Registers, m: Memory, cin: T.TextIO, cout: T.TextIO, max_zstrlen: int) -> None:
    start = m.load(r.SP - 4, 4)
    buffer = m.load_bytes(start, max_zstrlen)
    _bytes = buffer[0 : buffer.find(0)]
    cout.write(ascii_safe_encode(_bytes))


def print_top_i(r: Registers, m: Memory, cin: T.TextIO, cout: T.TextIO, max_zstrlen: int) -> None:
    i = m.load(r.SP - 4, 4)
    cout.write(f"{i}")


def print_top_x(r: Registers, m: Memory, cin: T.TextIO, cout: T.TextIO, max_zstrlen: int) -> None:
    i = m.load(r.SP - 4, 4)
    cout.write(f"0x{i:08x}")


def print_registers(r: Registers, m: Memory, cin: T.TextIO, cout: T.TextIO, max_zstrlen: int) -> None:
    cout.write(str(r))


def print_memory(r: Registers, m: Memory, cin: T.TextIO, cout: T.TextIO, max_zstrlen: int) -> None:
    start = m.load(r.SP - 8, 4)
    count = m.load(r.SP - 4, 4)
    cout.write("\n".join(hexdump_bytes(m.load_bytes(start, count))))
