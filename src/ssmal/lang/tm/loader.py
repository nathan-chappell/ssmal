from dataclasses import dataclass, replace
import logging
from typing import Generator

from ssmal.processors.processor import Processor

log = logging.getLogger(__name__)


@dataclass
class Section:
    name: str
    start: int
    end: int
    data: bytes
    monitor: bool = False


@dataclass
class TmLoader:
    text_bytes: bytes
    alignment: int = 0x100
    data_bytes: bytes = b""
    bss_size: int = 0
    monitor_text_area: bool = True
    monitor_data_area: bool = False

    log = log

    @property
    def sections(self) -> Generator[Section, None, None]:
        _offset = 0

        def _advance(count: int):
            nonlocal _offset
            _offset += count
            _offset += self.alignment - (count % self.alignment)

        text_offset = _offset
        _advance(len(self.text_bytes))
        yield Section("text", text_offset, _offset, self.text_bytes, self.monitor_text_area)

        data_offset = _offset
        _advance(len(self.data_bytes))
        yield Section("data", data_offset, _offset, self.data_bytes, self.monitor_data_area)

        bss_offset = _offset
        _advance(self.bss_size)
        yield Section("bss", bss_offset, _offset, b"\x00" * (_offset - bss_offset), True)

    def load_program(self, processor: Processor):
        sections = {section.name: section for section in self.sections}
        for section in sections.values():
            self.log.debug(replace(section, data=b''))
            processor.memory.store_bytes(section.start, section.data)
            if section.monitor:
                processor.memory.monitor(section.start, section.start + len(section.data))

        _stack_start = max(section.end for section in sections.values())

        processor.registers.IP = 0
        processor.registers.SP = _stack_start
        processor.registers.B = sections["data"].start
