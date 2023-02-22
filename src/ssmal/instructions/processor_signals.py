from ssmal.components.memory import Memory
from ssmal.components.registers import Registers


class ProcessorSignal(Exception):
    registers: Registers
    memory: Memory

    def __init__(self, registers: Registers, memory: Memory, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.registers = registers
        self.memory = memory


# fmt: off
class HaltSignal(ProcessorSignal): ...
class DebugSignal(ProcessorSignal): ...
class SysSignal(ProcessorSignal): ...
