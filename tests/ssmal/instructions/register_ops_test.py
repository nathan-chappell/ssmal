import pytest

import ssmal.instructions.register_ops as op

from ssmal.components.memory import Memory
from ssmal.components.registers import Registers


@pytest.mark.parametrize(
    "op_name, registers, expected",
    [
        ("SWPAB", Registers(A=3, B=4), Registers(A=4, B=3)),
        ("SWPAS", Registers(A=3, SP=14), Registers(A=14, SP=3)),
        ("SWPAI", Registers(A=3, IP=17), Registers(A=17, IP=3)),
    ],
)
def test_br(op_name: str, registers: Registers, expected: Registers):
    m = Memory()
    op.__dict__[op_name](registers, m)
    assert registers == expected
