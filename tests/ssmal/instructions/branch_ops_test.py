import pytest

import ssmal.instructions.branch_ops as op

from ssmal.components.memory import Memory
from ssmal.components.registers import Registers


@pytest.mark.parametrize(
    "op_name, A, B, i, expected_IP",
    [
        ("BRi", 0, 0, 13, 13),
        ("BRa", 14, 0, 0, 14),
        ("BRZi", 0, 0, 14, 14),
        ("BRZi", 1, 0, 14, 5),
        ("BRNi", -1, 0, 14, 14),
        ("BRNi", 0, 0, 14, 5),
        ("BRZb", 0, 14, 0, 14),
        ("BRZb", 1, 0, 0, 1),
        ("BRNb", -1, 14, 0, 14),
        ("BRNb", 0, 0, 0, 1),
    ],
)
def test_br(op_name: str, A: int, B: int, i: int, expected_IP: int):
    m = Memory()
    m.store(1, i)
    r = Registers(A=A, B=B)
    op.__dict__[op_name](r, m)
    assert r.IP == expected_IP
