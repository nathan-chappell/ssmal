
from processors.processor import Processor
from instructions.processor_signals import HaltSignal, DebugSignal


class Debugger:
    processor: Processor
    halt_signal: HaltSignal

    def run(self):
        while True:
            try:
                self.advance()
            except HaltSignal as halt:
                self.halt_signal = halt
                return
            except DebugSignal:
                self.on_break()

    def advance(self):
        self.processor.advance()
        ...
    
    def on_break(self):
        ...