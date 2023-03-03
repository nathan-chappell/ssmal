import io

from ssmal.lang.tm.transtion import TmTransition

class TmCompiler:
    assembly: io.StringIO

    def __init__(self) -> None:
        self.assembly = io.StringIO()

    def compile(self, transitions: list[TmTransition]) -> None:
        for transition in transitions:
            ...
            
        