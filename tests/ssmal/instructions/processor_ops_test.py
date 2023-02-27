import pytest

import ssmal.instructions.processor_ops as op

from ssmal.components.memory import Memory
from ssmal.components.registers import Registers


def test_HALT():
    m = Memory()
    r = Registers()
    with pytest.raises(op.HaltSignal):
        op.HALT(r, m)
