import io


from ssmal.components.memory import Memory
from ssmal.components.registers import Registers
from ssmal.instructions.processor_signals import SysSignal


def SYS(r: Registers, m: Memory) -> None:
    raise SysSignal(r, m)
