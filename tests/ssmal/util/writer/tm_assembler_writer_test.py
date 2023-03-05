import pytest

from ssmal.util.writer.tm_assembler_writer import TmAssemblerWriter
from ssmal.assemblers.tokenizer import tokenize
from ssmal.assemblers.assembler import Assembler

from ssmal.processors.processor import Processor


def test_save_restore_B():
    tm_assembler_writer = TmAssemblerWriter()
    tm_assembler_writer.save_B().restore_B()
    assembler = Assembler(list(tokenize(tm_assembler_writer.text)))
    assembler.assemble()
    p = Processor()
    r = p.registers
    _B = 31
    _A = 13
    r.A, r.B, r.SP = _A, _B, 0x20
    p.memory.store_bytes(0, assembler.buffer.getvalue())

    p.advance(steps=3)
    assert r.IP == 3
    assert (r.A, r.B) == (_A, _B)
    assert p.memory.load(r.SP - 4) == _B


@pytest.mark.parametrize("head", [0, 1, 2])
def test_three_way_switch(head: int):
    _state = "foo"
    _case_0 = 0x40
    _case_1 = 0x60
    _case_2 = 0x80

    tm_assembler_writer = TmAssemblerWriter()
    # fmt: off
    (tm_assembler_writer
        .label_state(_state)
        .three_way_switch(_state)
        .write_line(f".goto {_case_0}").label_case(_state, '0').indent().write_line('"CASE_0"').dedent()
        .write_line(f".goto {_case_1}").label_case(_state, '1').indent().write_line('"CASE_1"').dedent()
        .write_line(f".goto {_case_2}").label_case(_state, '2').indent().write_line('"CASE_2"').dedent())
    # fmt: on
    print(tm_assembler_writer.text)
    assembler = Assembler(list(tokenize(tm_assembler_writer.text)))
    assembler.assemble()
    p = Processor()
    p.memory.store_bytes(0, assembler.buffer.getvalue())
    p.memory.dump()
    p.registers.B = 0x60
    p.memory.store(0x60, head)
    p.advance(steps=2)
    assert p.registers.A == head - 1
    if head == 0:
        p.advance()
        assert p.registers.IP == _case_0
    elif head == 1:
        p.advance(steps=2)
        assert p.registers.IP == _case_1
    elif head == 2:
        p.advance(steps=3)
        assert p.registers.IP == _case_2
