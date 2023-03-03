from pprint import pformat

from ssmal.components.memory import Memory
from ssmal.components.registers import Registers
from ssmal.util.hexdump_bytes import hexdump_bytes


class ProcessorSignal(Exception):
    registers: Registers
    memory: Memory

    def __init__(self, registers: Registers, memory: Memory, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.registers = registers
        self.memory = memory

    def _get_memory_lines(self, _from, _to) -> list[str]:
        assert _from < _to
        _from = max(0, _from)
        return list(hexdump_bytes(self.memory.load_bytes(_from, _to - _from), start_offset=_from))

    def __str__(self) -> str:
        r = self.registers
        _A = f"A:  {r.A:12} (0x{r.A:08x})"
        _B = f"B:  {r.B:12} (0x{r.B:08x})"
        _IP = f"IP: {r.IP:12} (0x{r.IP:08x})"
        _SP = f"SP: {r.SP:12} (0x{r.SP:08x})"

        CONTEXT_WIDTH = 0x80
        _context_before = self._get_memory_lines(r.IP - CONTEXT_WIDTH, r.IP)
        _context_after = self._get_memory_lines(r.IP, r.IP + CONTEXT_WIDTH)

        return "\n".join(
            ["", _A, _B, _IP, _SP, "--- memory dump ---", *_context_before, "IP >>>", *_context_after, "--- end memory dump ---"]
        )


# fmt: off
class HaltSignal(ProcessorSignal): ...
class DebugSignal(ProcessorSignal): ...
class SysSignal(ProcessorSignal): ...
class TrapSignal(ProcessorSignal): ...
