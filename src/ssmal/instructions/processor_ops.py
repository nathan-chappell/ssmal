from ssmal.components.memory import Memory
from ssmal.components.registers import Registers
from ssmal.instructions.processor_signals import HaltSignal, DebugSignal

# fmt: off
def DBG(r: Registers, m: Memory) -> None: raise DebugSignal(r,m)
def HALT(r: Registers, m: Memory) -> None: raise HaltSignal(r,m)
def NOP(r: Registers, m: Memory) -> None: return
