from dataclasses import dataclass
import typing as T
import re

from ssmal.processors.processor import Processor
from ssmal.instructions.processor_signals import HaltSignal, DebugSignal


class DebugParseError(Exception):
    ...


@dataclass
class DebuggerCommand:
    command: T.Literal["print", "breakpoint", "step"]
    argument: int = 0

    _command_regex = re.compile(r"^ *(?<command>p|print|b|breakpoint|s|step) *(?<argument>\d+)? *$")

    @classmethod
    def fix_command(cls, command: str) -> T.Literal["print", "breakpoint", "step"]:
        # fmt: off
        if command == 'p':          return 'print'
        if command == 'print':      return 'print'
        if command == 'b':          return 'breakpoint'
        if command == 'breakpoint': return 'breakpoint'
        if command == 's':          return 'step'
        if command == 'step':       return 'step'
        # fmt: on
        raise DebugParseError(f"invalid debugger command: {command}")

    @classmethod
    def fix_argument(cls, argument: T.Optional[str]) -> int:
        if argument is None:
            return 0
        try:
            if argument.startswith("0x"):
                return int(argument, 16)
            else:
                return int(argument)
        except ValueError as e:
            raise DebugParseError(e.args[0])

    @classmethod
    def parse_command(cls, line: str) -> "DebuggerCommand":
        match = cls._command_regex.match(line)
        if match:
            command = cls.fix_command(match.group("command"))
            argument = cls.fix_argument(match.group("command"))
            return cls(command=command, argument=argument)
        else:
            raise DebugParseError(f"failed to parse line: {line}")


class Debugger:
    processor: Processor
    halt_signal: HaltSignal | None = None
    breakpoints: set[int]

    def __init__(self) -> None:
        self.processor = Processor()
        self.breakpoints = set[int]()

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
        if self.processor.registers.IP in self.breakpoints:
            raise DebugSignal(self.processor.registers, self.processor.memory)

    def on_break(self):
        self.write_message(self.processor.registers)
        _command = self.read_command()

    def write_message(self, any: T.Any):
        print(any)

    def read_command(self):
        while True:
            _input = input("> ")
            try:
                debugger_command = DebuggerCommand.parse_command(_input)
                if debugger_command.command == "print":
                    self.write_message(self.processor.memory.load_bytes(debugger_command.argument, 0x40))
                elif debugger_command.command == "breakpoint":
                    self.breakpoints.add(debugger_command.argument)
                elif debugger_command.command == "step":
                    for _ in range(debugger_command.argument):
                        self.advance()
            except DebugParseError as e:
                self.write_message(e)
            else:
                break
